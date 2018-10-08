#!/usr/bin/env python
import Monsoon.LVPM as LVPM
import Monsoon.HVPM as HVPM
from Monsoon import sampleEngine
import argparse
import csv
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
plt.ylabel('amperage (mA)')
plt.xlabel('time sequences')
plt.ylim((0, 2000))

display_range = 50000
samples_queue = collections.deque(maxlen=display_range)
time_queue = collections.deque(maxlen=display_range)

time_queue.extend([0 for _ in range(display_range)])
samples_queue.extend([0 for _ in range(display_range)])
line, = ax.plot(time_queue, samples_queue, linewidth=0.5)

should_pause = False
csv_file_handle = None
csv_writer = None
trigger_count = 0
trigger = float("inf")
triggered = False
header = ["Time(ms)", "Main(mA)", "Main Voltage(V)"]


def animate(_):
    if should_pause:
        return line,
    # print("samples: {}".format(latest_current_values))
    line.set_xdata(time_queue)
    line.set_ydata(samples_queue)  # update the data
    ax.relim()
    for label in ax.xaxis.get_ticklabels()[::100]:
        label.set_visible(False)
    ax.autoscale_view(True, True, True)
    return line,


def sample_generator(sampler, sample_number_):
    sampler.startSampling(sample_number_, output_callback=samples_callback)


def samples_callback(samples_):
    last_values = samples_[sampleEngine.channels.MainCurrent]
    if last_values:
        # filter negative values
        valid_values = [max(v, 0) for v in last_values]
        time_queue.extend(samples_[sampleEngine.channels.timeStamp])
        samples_queue.extend(valid_values)
        avg = sum(valid_values) / len(valid_values)
        global triggered
        if avg > trigger:
            global csv_file_handle, csv_writer
            if csv_file_handle:
                print("recording", avg, len(valid_values))

                records = list(zip(samples_[sampleEngine.channels.timeStamp],
                                   samples_[sampleEngine.channels.MainCurrent],
                                   samples_[2]))
                if not csv_writer:
                    csv_writer = csv.writer(csv_file_handle)
                    csv_writer.writerow(header)
                csv_writer.writerows(records)
                triggered = True
        else:
            if triggered and csv_file_handle:
                print("stopped trigger")
                csv_file_handle.close()
                csv_file_handle = None


def on_click(_event):
    global should_pause
    if _event.dblclick:
        should_pause ^= True


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--number_of_samples", type=int, default=-1,
                        help="number of power samples per second, default to -1 meaning sample infinitely")
    parser.add_argument("-m", "--monsoon_model", choices=("lvpm", "hvpm", "l", "h", "black", "white", "b", "w"),
                        default="w",
                        help="Monsoon type, either white(w,l,lvpm) or black(b,h,hvpm)")
    parser.add_argument("-s", "--save_file", type=str, default=None,  # 'data/power_samples.csv',
                        help="file to save power samples")
    parser.add_argument("-t", "--trigger", type=float, default=float("inf"),
                        help="threshold to trigger sampling, unit is mA")

    args = parser.parse_args()
    sample_number = args.number_of_samples if args.number_of_samples > 0 else sampleEngine.triggers.SAMPLECOUNT_INFINITE
    monsoon_model = args.monsoon_model

    if monsoon_model.startswith('l') or monsoon_model.startswith('w'):
        monsoon = LVPM.Monsoon()  # white
    else:
        monsoon = HVPM.Monsoon()
    monsoon.setup_usb()
    print("Monsoon Power Monitor Serial number: {}".format(monsoon.getSerialNumber()))
    engine = sampleEngine.SampleEngine(monsoon)
    trigger = args.trigger
    if args.save_file:
        dir_name = os.path.dirname(args.save_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if trigger < float("inf"):  # set trigger
            engine.disableCSVOutput()
            # global csv_name
            csv_file = args.save_file
            csv_file_handle = open(csv_file, 'w')
        else:
            engine.enableCSVOutput(args.save_file)
    else:
        engine.disableCSVOutput()
    engine.ConsoleOutput(True)


    def signal_handler(_signal, _frame):
        print('You pressed Ctrl+C, clearing monsoon sampling and exit!')
        monsoon.stopSampling()
        sys.exit(0)


    def handle_close(_event):
        print('You cosed figure, clearing monsoon sampling and exit!')
        monsoon.stopSampling()
        sys.exit(0)


    fig.canvas.mpl_connect('close_event', handle_close)
    fig.canvas.mpl_connect('button_press_event', on_click)

    signal.signal(signal.SIGINT, signal_handler)

    pt = threading.Thread(target=sample_generator, name='sample_generator', args=(engine, sample_number))
    pt.daemon = True
    pt.start()

    ani = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()
