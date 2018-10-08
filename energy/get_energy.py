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
    powers = []
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            time_stamp = float(row[0])
            current = float(row[1])
            voltage = float(row[2])
            if voltage > 0:
                times.append(time_stamp)
                powers.append(current)

    duration = times[-1] - times[0]
    energy = np.trapz(np.asarray(powers, dtype=float), x=np.asarray(times, dtype=float))
    print('samples:', len(powers))
    print('duration: {:.3f} s'.format(duration))
    print('energy: {:.3f} mAh'.format(energy / 3600))
    print('power: {:.3f} mW'.format(energy / duration))
