"""
Run parameter sweep across modes and loss values, save CSV and plot results.

Produces files under: udp_optimizer_demo/results/
 - results.csv
 - delivered_vs_loss.png
 - goodput_vs_loss.png
 - overhead_vs_loss.png

This script imports `run_experiment` from `experiment.py` and runs experiments serially.
"""

import asyncio
import csv
import os
import statistics
from collections import defaultdict

from experiment import run_experiment


RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)


async def single_run(mode, loss, run_id, packets, payload, fec_group, timeout):
    r = await run_experiment(mode=mode, loss=loss, packets=packets, payload=payload,
                             fec_group=fec_group, arq_timeout=timeout)
    # attach meta
    r.update({'mode': mode, 'loss': loss, 'run': run_id, 'packets_requested': packets})
    return r


def aggregate_results(rows):
    # rows: list of dicts
    agg = defaultdict(list)
    for r in rows:
        key = (r['mode'], r['loss'])
        agg[key].append(r)

    summary = []
    for (mode, loss), runs in sorted(agg.items()):
        # use .get defaults to handle error/timeout rows
        delivered = [x.get('delivered_packets', 0) for x in runs]
        goodput = [x.get('goodput_bytes_per_sec', 0.0) for x in runs]
        overhead = [ (x.get('sent_packets', 0) - x.get('packets_requested', 0))/max(1,x.get('sent_packets', 1)) for x in runs]
        summary.append({
            'mode': mode,
            'loss': loss,
            'runs': len(runs),
            'delivered_mean': statistics.mean(delivered),
            'delivered_stdev': statistics.pstdev(delivered) if len(delivered)>1 else 0.0,
            'goodput_mean': statistics.mean(goodput),
            'goodput_stdev': statistics.pstdev(goodput) if len(goodput)>1 else 0.0,
            'overhead_mean': statistics.mean(overhead),
            'overhead_stdev': statistics.pstdev(overhead) if len(overhead)>1 else 0.0,
        })
    return summary


def save_csv(rows, path):
    keys = ['mode','loss','run','packets_requested','sent_packets','retransmissions','delivered_packets','fec_recoveries','duration_sec','goodput_bytes','goodput_bytes_per_sec']
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in keys})


def try_plot(summary, outdir):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except Exception:
        print('matplotlib or numpy not available — skipping plots. Install with: pip install matplotlib numpy')
        return

    # delivered vs loss
    modes = sorted({s['mode'] for s in summary})
    losses = sorted({s['loss'] for s in summary})

    plt.figure()
    for m in modes:
        xs = [s['loss'] for s in summary if s['mode']==m]
        ys = [s['delivered_mean'] for s in summary if s['mode']==m]
        yerr = [s['delivered_stdev'] for s in summary if s['mode']==m]
        plt.errorbar(xs, ys, yerr=yerr, marker='o', label=m)
    plt.xlabel('loss probability')
    plt.ylabel('delivered packets (mean)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(outdir, 'delivered_vs_loss.png'))
    plt.close()

    # goodput vs loss
    plt.figure()
    for m in modes:
        xs = [s['loss'] for s in summary if s['mode']==m]
        ys = [s['goodput_mean'] for s in summary if s['mode']==m]
        yerr = [s['goodput_stdev'] for s in summary if s['mode']==m]
        plt.errorbar(xs, ys, yerr=yerr, marker='o', label=m)
    plt.xlabel('loss probability')
    plt.ylabel('goodput bytes/sec (mean)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(outdir, 'goodput_vs_loss.png'))
    plt.close()

    # overhead vs loss
    plt.figure()
    for m in modes:
        xs = [s['loss'] for s in summary if s['mode']==m]
        ys = [s['overhead_mean'] for s in summary if s['mode']==m]
        yerr = [s['overhead_stdev'] for s in summary if s['mode']==m]
        plt.errorbar(xs, ys, yerr=yerr, marker='o', label=m)
    plt.xlabel('loss probability')
    plt.ylabel('transmission overhead (mean fraction)')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(outdir, 'overhead_vs_loss.png'))
    plt.close()


def main():
    modes = ['baseline','arq','fec']
    losses = [0.0, 0.01, 0.05, 0.1, 0.2]
    runs_per_point = 3
    packets = 200
    payload = 200
    fec_group = 4
    timeout = 0.1

    rows = []

    async def batch():
        # per-run timeout to avoid hangs; if a run times out we record an error row
        per_run_timeout = 20.0  # seconds
        for m in modes:
            for loss in losses:
                for run_id in range(1, runs_per_point+1):
                    print(f'Running mode={m} loss={loss} run={run_id}')
                    try:
                        r = await asyncio.wait_for(single_run(m, loss, run_id, packets, payload, fec_group, timeout), timeout=per_run_timeout)
                    except asyncio.TimeoutError:
                        print(f'Run timed out: mode={m} loss={loss} run={run_id}')
                        r = {'mode': m, 'loss': loss, 'run': run_id, 'packets_requested': packets, 'error': 'timeout'}
                    except Exception as e:
                        print(f'Run error: mode={m} loss={loss} run={run_id} -> {e}')
                        r = {'mode': m, 'loss': loss, 'run': run_id, 'packets_requested': packets, 'error': str(e)}
                    rows.append(r)
    asyncio.run(batch())

    csv_path = os.path.join(RESULTS_DIR, 'results.csv')
    save_csv(rows, csv_path)
    print('Saved CSV to', csv_path)

    summary = aggregate_results(rows)
    try_plot(summary, RESULTS_DIR)
    print('Saved plots to', RESULTS_DIR)


if __name__ == '__main__':
    main()
