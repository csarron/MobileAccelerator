#!/usr/bin/env python

import argparse
import numpy as np
import csv


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=str, default=None,  # 'data/power_samples.csv',
                        help="file to load power samples")

    args = parser.parse_args()
    csv_file = args.csv_file
    times = []
    currents = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            time_stamp = row[0]
            amp = row[1]
            voltage = row[2]
            if voltage > 0:
                times.append(time_stamp)
                currents.append(amp)
    print(len(times), len(currents))
    print(np.trapz(np.asarray(currents, dtype=float), x=np.asarray(times, dtype=float)))
