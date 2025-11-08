# Results explanation / Giải thích kết quả

This file explains the JSON summary printed by `experiment.py` and shows how to interpret the sample output you saw.

---

## Keys in the summary (what each metric means)

- `mode` — the experiment mode run: `baseline`, `arq` or `fec`.

- `loss` — packet loss probability used by the emulator (0.0–1.0). This is the probability that any single packet (including ACKs) is dropped.

- `delay_mean` — mean one-way delay (seconds) used by the emulator. Jitter is applied around this mean.

- `packets_requested` — number of data packets the sender attempted to send (application-level data packets).

- `sent_packets` — total number of packets injected into the emulator by the sender. This includes:
  - all data packets, and
  - FEC parity packets (when `mode == fec`), or
  - any retransmissions sent by ARQ (when `mode == arq`).

- `retransmissions` — number of retransmission attempts performed by the sender's ARQ logic. Note: when `mode == fec`, `retransmissions` will normally be 0 because FEC mode does not perform retransmits in this demo.

- `delivered_packets` — number of distinct data packets that the receiver ended up with (including packets recovered by FEC). This value is measured at the receiver's application layer (how many payloads are available for use).

- `fec_recoveries` — when running in `fec` mode, the number of data packets the receiver recovered using parity (XOR) rather than receiving them directly. Each recovery corresponds to a single lost data packet that was reconstructed using the parity packet and the remaining group members.

- `duration_sec` — wall-clock time (seconds) spent by the experiment (sender start → receiver finish). It includes send time and a short drain period for in-flight packets.

- `goodput_bytes` — the total number of payload bytes the receiver successfully delivered to the application (sum of lengths of recovered/delivered payloads). Parity packets do not contribute to goodput.

- `goodput_bytes_per_sec` — `goodput_bytes / duration_sec`; a simple estimate of observed application-layer throughput.

---

## Interpreting the sample output (example values)

Sample run printed the following summary (trimmed):

{
  "mode": "fec",
  "loss": 0.05,
  "packets_requested": 50,
  "sent_packets": 63,
  "retransmissions": 0,
  "delivered_packets": 50,
  "fec_recoveries": 8,
  "duration_sec": 0.3246,
  "goodput_bytes": 9800,
  "goodput_bytes_per_sec": 30190.47
}

Explanation:

- `packets_requested = 50`: the application asked the sender to transmit 50 data packets.

- `sent_packets = 63`: more packets were sent than requested because in FEC mode the sender transmits parity packets in addition to the 50 data packets. With a FEC group size of 4 you get one parity packet per group. For 50 data packets and group size 4 the parity count is `ceil(50 / 4) = 13`. So total transmitted = 50 data + 13 parity = 63, exactly matching the reported `sent_packets`.

- `retransmissions = 0`: the demo's FEC mode does not perform ARQ retransmissions, so no retransmissions were needed/attempted.

- `delivered_packets = 50`: the receiver ended up with all 50 application data payloads available (some were received directly, others reconstructed by parity). This is the main user-visible success metric — how many messages the application can consume.

- `fec_recoveries = 8`: out of the 50 data packets, 8 were lost in transit but successfully reconstructed by the parity bytes. That means for those 8 packets the receiver did not get the original data packet, but was able to rebuild it using the parity and the other packets in the group.

- `goodput_bytes = 9800`: the receiver observed 9,800 bytes of payload delivered. In theory, if payload size was 200 bytes and all 50 packets were delivered, expected would be `50 * 200 = 10,000` bytes. Small differences can arise because of how the example payloads are constructed or for the final partial group (the demo may send smaller final payloads or use different payload length in some runs). Treat `goodput_bytes` as the measured application-layer bytes delivered in that run.

- `goodput_bytes_per_sec = 30190.47`: measured goodput = `goodput_bytes / duration_sec`. It gives an estimate of useful payload throughput for that run.

Important notes when you compare runs

- `sent_packets` is not equal to `packets_requested` under FEC because parity packets are extra overhead. When comparing modes, compare useful delivered bytes or `delivered_packets` and consider overhead separately.

- `fec_recoveries` is the count of lost packets that were successfully reconstructed by FEC alone. If `fec_recoveries` is high relative to `packets_requested`, it means FEC helped deliver packets that would otherwise be lost.

- The demo's `baseline` mode will show `sent_packets == packets_requested` but typically `delivered_packets` will drop as `loss` increases. `arq` mode will show `retransmissions > 0` and may maintain higher `delivered_packets` at the cost of extra retransmitted bytes and longer `duration_sec`.

- To evaluate efficiency, compute effective overhead and net-goodput. Example metrics you can derive:
  - parity overhead = (sent_packets - packets_requested) / sent_packets
  - recovery rate = fec_recoveries / packets_requested
  - bytes per second = goodput_bytes_per_sec
## 066203009953 - Tran The Hao
---

