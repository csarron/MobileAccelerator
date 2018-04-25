#!/usr/bin/env python
import Monsoon.LVPM as LVPM
import Monsoon.HVPM as HVPM
import Monsoon.sampleEngine as sampleEngine
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number_of_samples", type=int, default=1000,
                        help="number of power samples per second")
    parser.add_argument("-t", "--type", choices=("lvpm", "hvpm", "l", "h", "black", "white", "b", "w"), default="w",
                        help="Monsoon type, either white(w,l,lvpm) or black(b,h,hvpm)")
    parser.add_argument("-s", "--save_file", type=str, default='data/power_samples.csv',
                        help="number of power samples per second")
    args = parser.parse_args()
    sample_number = args.number_of_samples
    monsoon_type = args.type
    if monsoon_type.startswith('l') or monsoon_type.startswith('w'):
        monsoon = LVPM.Monsoon() # whilte
    else:
        monsoon = HVPM.Monsoon()
    monsoon.setup_usb()
    engine = sampleEngine.SampleEngine(monsoon)
    engine.enableCSVOutput(args.save_file)

    engine.ConsoleOutput(True)
    print("Monsoon Power Monitor Serial number: {}".format(monsoon.getSerialNumber()))
    engine.startSampling(sample_number)
