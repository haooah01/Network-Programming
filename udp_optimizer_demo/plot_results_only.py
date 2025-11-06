"""
Load an existing CSV produced by sweep_and_plot.py and produce the three plots.
This avoids re-running experiments when the CSV already exists.
"""
import csv
import os
import ast

from sweep_and_plot import aggregate_results, try_plot

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
CSV_PATH = os.path.join(RESULTS_DIR, 'results.csv')

def read_rows(path):
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # convert numeric fields where possible
            def to_number(v):
                if v is None:
                    return None
                s = str(v).strip()
                if s == '':
                    return None
                s = s.replace(',','')
                try:
                    iv = int(s)
                    return iv
                except Exception:
                    try:
                        fv = float(s)
                        return fv
                    except Exception:
                        return None

            for k in ['loss','run','packets_requested','sent_packets','retransmissions','delivered_packets','fec_recoveries']:
                if k in r:
                    num = to_number(r[k])
                    if num is not None:
                        r[k] = num
            for k in ['duration_sec','goodput_bytes','goodput_bytes_per_sec']:
                num = to_number(r.get(k))
                r[k] = float(num) if num is not None else 0.0

            # ensure integer keys exist and are numeric (default 0)
            for k in ['run','packets_requested','sent_packets','retransmissions','delivered_packets','fec_recoveries']:
                num = to_number(r.get(k))
                r[k] = int(num) if (num is not None) else 0
            rows.append(r)
    return rows

def main():
    if not os.path.exists(CSV_PATH):
        print('CSV not found:', CSV_PATH)
        return
    rows = read_rows(CSV_PATH)
    summary = aggregate_results(rows)
    try_plot(summary, RESULTS_DIR)
    print('Plots written to', RESULTS_DIR)

if __name__ == '__main__':
    main()
