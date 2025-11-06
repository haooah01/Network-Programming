#!/usr/bin/env python3
"""
UDP Optimization Demo

Simple in-process asyncio simulator demonstrating:
 - baseline UDP (no reliability)
 - ARQ (selective retransmit)
 - simple XOR-parity FEC (group k data packets + 1 parity)

Run: python experiment.py --mode fec --loss 0.1 --packets 100

This script is intentionally self-contained so you can run single-file experiments.
"""

import argparse
import os
import asyncio
import json
import random
import time
from collections import defaultdict


class Emulator:
    """Simulate an unreliable network between sender and receiver.

    The emulator receives tuples (dst, pkt) from the sender or receiver and forwards
    them to the other side after applying loss and delay. ACKs go through the same
    pipeline so they may be lost/delayed.
    """

    def __init__(self, loss_prob=0.0, delay_mean=0.02, delay_jitter=0.01):
        self.loss = loss_prob
        self.delay_mean = delay_mean
        self.delay_jitter = delay_jitter
        self._queue = asyncio.Queue()

    async def send(self, payload, to):
        """Offer a packet into the emulator; it will be scheduled for delivery."""
        # decide to drop
        if random.random() < self.loss:
            # dropped
            return

        delay = max(0.0, random.gauss(self.delay_mean, self.delay_jitter))

        async def deliver():
            await asyncio.sleep(delay)
            await to.put(payload)

        asyncio.create_task(deliver())


class Receiver:
    """Receiver collects delivered packets and performs FEC recovery/ACKing."""

    def __init__(self, emulator, in_queue, ack_queue, mode='baseline', fec_group=4):
        self.emu = emulator
        self.in_q = in_queue
        self.ack_q = ack_queue
        self.mode = mode
        self.fec_group = fec_group
        self.received = {}  # seq -> payload bytes
        # group_id -> dict with keys: int seq -> {'payload': bytes}, and optional '__parity__' -> bytes
        self.groups = defaultdict(dict)
        self.fec_recoveries = 0

    async def run(self):
        while True:
            pkt = await self.in_q.get()
            if pkt is None:
                break

            typ = pkt.get('type')
            if typ == 'data':
                seq = pkt['seq']
                payload = pkt['payload']
                # store received payload
                self.received[seq] = payload

                if self.mode in ('arq',):
                    # send ACK back
                    ack = {'type': 'ack', 'seq': seq}
                    await self.emu.send(ack, self.ack_q)

                # FEC handling: keep group payloads and optional parity separate
                if self.mode == 'fec':
                    gid = pkt.get('group', seq // max(1, self.fec_group))
                    if pkt.get('is_parity'):
                        # store parity under special key
                        self.groups[gid]['__parity__'] = pkt.get('parity')
                    else:
                        self.groups[gid][seq] = {'payload': payload}

                    # attempt recovery if parity present
                    group_map = self.groups[gid]
                    if '__parity__' in group_map:
                        expected = list(range(gid * self.fec_group, gid * self.fec_group + self.fec_group))
                        present = set(k for k in group_map.keys() if isinstance(k, int))
                        missing = [s for s in expected if s not in present]
                        if len(missing) == 1:
                            parity_bytes = group_map['__parity__']
                            recovered = bytearray(parity_bytes)
                            for s in expected:
                                if s in group_map:
                                    pb = group_map[s]['payload']
                                    for i in range(len(recovered)):
                                        recovered[i] ^= pb[i]
                            # store recovered payload
                            self.received[missing[0]] = bytes(recovered)
                            self.fec_recoveries += 1

            elif typ == 'control' and pkt.get('cmd') == 'stop':
                break

    def stats(self):
        return {'delivered_packets': len(self.received), 'fec_recoveries': self.fec_recoveries}


class Sender:
    """Base sender class; derived classes implement specific strategies."""

    def __init__(self, emulator, out_q, ack_q, packets=100, payload_size=100):
        self.emu = emulator
        self.out_q = out_q
        self.ack_q = ack_q
        self.packets = packets
        self.payload_size = payload_size
        self.sent = 0
        self.retransmissions = 0

    async def send_packet(self, pkt):
        await self.emu.send(pkt, self.out_q)
        self.sent += 1


class SenderBaseline(Sender):
    async def run(self):
        # send N data packets quickly
        for seq in range(self.packets):
            payload = bytes([seq % 256]) * self.payload_size
            pkt = {'type': 'data', 'seq': seq, 'payload': payload}
            await self.send_packet(pkt)
            # small pacing
            await asyncio.sleep(0)


class SenderARQ(Sender):
    def __init__(self, *args, timeout=0.1, max_retries=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout
        self.max_retries = max_retries

    async def run(self):
        pending = {}  # seq -> (payload, retries)

        async def listener():
            while True:
                ack = await self.ack_q.get()
                if ack is None:
                    break
                if ack.get('type') == 'ack':
                    seq = ack['seq']
                    pending.pop(seq, None)

        listener_task = asyncio.create_task(listener())

        for seq in range(self.packets):
            payload = bytes([seq % 256]) * self.payload_size
            pending[seq] = (payload, 0)
            await self.send_packet({'type': 'data', 'seq': seq, 'payload': payload})

        # retransmit loop until pending empty or retries exhausted
        start = time.time()
        while pending:
            to_remove = []
            for seq, (payload, retries) in list(pending.items()):
                if retries >= self.max_retries:
                    to_remove.append(seq)
                    continue
                # retransmit
                pending[seq] = (payload, retries + 1)
                self.retransmissions += 1
                await self.send_packet({'type': 'data', 'seq': seq, 'payload': payload})
            for r in to_remove:
                pending.pop(r, None)
            await asyncio.sleep(self.timeout)

        listener_task.cancel()


class SenderFEC(Sender):
    def __init__(self, *args, fec_group=4, **kwargs):
        super().__init__(*args, **kwargs)
        self.fec_group = fec_group

    async def run(self):
        group = []
        for seq in range(self.packets):
            payload = bytes([seq % 256]) * self.payload_size
            pkt = {'type': 'data', 'seq': seq, 'payload': payload, 'group': seq // self.fec_group}
            group.append((seq, payload))
            await self.send_packet(pkt)
            if len(group) == self.fec_group:
                # compute parity (XOR across payloads)
                parity = bytearray(self.payload_size)
                for _, pb in group:
                    for i in range(self.payload_size):
                        parity[i] ^= pb[i]
                parity_pkt = {'type': 'data', 'seq': -1, 'payload': b'', 'is_parity': True,
                              'group': group[0][0] // self.fec_group, 'parity': bytes(parity)}
                await self.send_packet(parity_pkt)
                group = []

        # send remaining group's parity if partial
        if group:
            parity = bytearray(self.payload_size)
            for _, pb in group:
                for i in range(self.payload_size):
                    parity[i] ^= pb[i]
            parity_pkt = {'type': 'data', 'seq': -1, 'payload': b'', 'is_parity': True,
                          'group': group[0][0] // self.fec_group, 'parity': bytes(parity)}
            await self.send_packet(parity_pkt)


async def run_experiment(mode='baseline', loss=0.05, delay=0.02, jitter=0.01,
                         packets=200, payload=200, fec_group=4, arq_timeout=0.1):
    emu = Emulator(loss_prob=loss, delay_mean=delay, delay_jitter=jitter)

    to_receiver = asyncio.Queue()
    to_sender_ack = asyncio.Queue()

    receiver = Receiver(emu, to_receiver, to_sender_ack, mode=mode, fec_group=fec_group)

    if mode == 'baseline':
        sender = SenderBaseline(emu, to_receiver, to_sender_ack, packets=packets, payload_size=payload)
    elif mode == 'arq':
        sender = SenderARQ(emu, to_receiver, to_sender_ack, packets=packets, payload_size=payload,
                           timeout=arq_timeout, max_retries=10)
    elif mode == 'fec':
        sender = SenderFEC(emu, to_receiver, to_sender_ack, packets=packets, payload_size=payload,
                           fec_group=fec_group)
    else:
        raise ValueError('unknown mode')

    # start receiver
    rtask = asyncio.create_task(receiver.run())
    # start sender
    stask = asyncio.create_task(sender.run())

    t0 = time.time()
    await stask
    # give some time for in-flight packets
    await asyncio.sleep(delay * 10 + 0.1)
    # stop receiver
    await emu.send({'type': 'control', 'cmd': 'stop'}, to_receiver)
    await rtask
    t1 = time.time()

    stats = {
        'mode': mode,
        'loss': loss,
        'delay_mean': delay,
        'packets_requested': packets,
        'sent_packets': sender.sent,
        'retransmissions': getattr(sender, 'retransmissions', 0),
        'delivered_packets': len(receiver.received),
        'fec_recoveries': receiver.fec_recoveries,
        'duration_sec': t1 - t0,
        'goodput_bytes': sum(len(v) for v in receiver.received.values()),
    }

    if stats['duration_sec'] > 0:
        stats['goodput_bytes_per_sec'] = stats['goodput_bytes'] / stats['duration_sec']
    else:
        stats['goodput_bytes_per_sec'] = 0.0

    return stats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['baseline', 'arq', 'fec'], default='baseline')
    parser.add_argument('--loss', type=float, default=0.05, help='packet loss probability')
    parser.add_argument('--delay', type=float, default=0.02, help='mean one-way delay (s)')
    parser.add_argument('--jitter', type=float, default=0.01, help='delay jitter (s)')
    parser.add_argument('--packets', type=int, default=200)
    parser.add_argument('--payload', type=int, default=200)
    parser.add_argument('--fec-group', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=0.1)
    parser.add_argument('--runs', type=int, default=1)
    parser.add_argument('--out', default='udp_experiment_results.json')

    args = parser.parse_args()

    # ensure output path is inside the demo folder by default
    out_path = args.out
    if not os.path.isabs(out_path):
        demo_dir = os.path.dirname(__file__)
        out_path = os.path.join(demo_dir, out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    results = []

    async def batch():
        for i in range(args.runs):
            print(f'Run {i+1}/{args.runs}: mode={args.mode}, loss={args.loss}')
            s = await run_experiment(mode=args.mode, loss=args.loss, delay=args.delay,
                                     jitter=args.jitter, packets=args.packets,
                                     payload=args.payload, fec_group=args.fec_group,
                                     arq_timeout=args.timeout)
            print(json.dumps(s, indent=2))
            results.append(s)

    asyncio.run(batch())

    # write results into the demo folder (or absolute path if provided)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f'Wrote results to {out_path}')


if __name__ == '__main__':
    main()
