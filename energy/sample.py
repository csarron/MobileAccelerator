#!/usr/bin/env python
import Monsoon.LVPM as LVPM
import Monsoon.HVPM as HVPM
from Monsoon import sampleEngine
import argparse
import os
import matplotlib

matplotlib.use('TKAgg')
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import threading
import collections
import signal
import sys

fig, ax = plt.subplots()

display_range = 50000
samples_queue = collections.deque(maxlen=display_range)
time_queue = collections.deque(maxlen=display_range)

time_queue.extend([0 for _ in range(display_range)])
samples_queue.extend([0 for _ in range(display_range)])
line, = ax.plot(time_queue, samples_queue)


def animate(_):
    # print("samples: {}".format(latest_current_values))
    line.set_xdata(time_queue)
    line.set_ydata(samples_queue)  # update the data
    ax.relim()
    for label in ax.xaxis.get_ticklabels()[::100]:
        label.set_visible(False)
    ax.autoscale_view(True, True, True)
    return line,


def sample_generator(sampler, arguments):
    sampler.enableCSVOutput(arguments.save_file)
    sampler.ConsoleOutput(True)
    sampler.startSampling(sample_number, granularity=10, output_callback=samples_callback)


def samples_callback(samples_):
    last_values = samples_[sampleEngine.channels.MainCurrent]
    if last_values:
        time_queue.extend(samples_[sampleEngine.channels.timeStamp])
        samples_queue.extend(last_values)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number_of_samples", type=int, default=1000,
                        help="number of power samples per second")
    parser.add_argument("-t", "--type", choices=("lvpm", "hvpm", "l", "h", "black", "white", "b", "w"), default="w",
                        help="Monsoon type, either white(w,l,lvpm) or black(b,h,hvpm)")
    parser.add_argument("-s", "--save_file", type=str, default='data/power_samples.csv',
                        help="number of power samples per second")
    args = parser.parse_args()
    sample_number = args.number_of_samples if args.number_of_samples > 0 else sampleEngine.triggers.SAMPLECOUNT_INFINITE
    machine_type = args.type
    dir_name = os.path.dirname(args.save_file)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if machine_type.startswith('l') or machine_type.startswith('w'):
        monsoon = LVPM.Monsoon()  # white
    else:
        monsoon = HVPM.Monsoon()
    monsoon.setup_usb()


    def signal_handler(signal, frame):
        print('You pressed Ctrl+C, clearing monsoon sampling and exit!')
        monsoon.stopSampling()
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)
    print("Monsoon Power Monitor Serial number: {}".format(monsoon.getSerialNumber()))
    engine = sampleEngine.SampleEngine(monsoon)
    pt = threading.Thread(target=sample_generator, name='sample_generator', args=(engine, args))
    pt.daemon = True
    pt.start()

    ani = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()
