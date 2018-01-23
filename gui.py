"""GUI, mostly spaghetti

Called like this from command line:
python3 gui.py DATA.csv
"""

import tkinter as tk
import os
from sys import argv

from rocket import Rocket

top = tk.Tk()
timeLabel = tk.Label(top)
altLabel = tk.Label(top)
velLabel = tk.Label(top)
stateLabel = tk.Label(top)
indexLabel = tk.Label(top)


def display(state, time, velocity, altitude):
    timeLabel.config(text="Time: {:.3f}".format(time))
    altLabel.config(text="Altitude: {:.3f}".format(altitude))
    velLabel.config(text="Velocity: {:.3f}".format(velocity))
    indexLabel.config(text="Line: {}".format(index+1))
    if state:
        stateLabel.config(text="State: {}".format(state))


rocket = Rocket(os.getcwd() + "/" + argv[1])
start_status = {
    'time': rocket.state.last_time,
    'altitude': rocket.state.last_alt,
    'velocity': rocket.state.last_alt
}
start_state = type(rocket.state).__name__
prev, index = [(start_state, start_status)], 0
display(start_state, **start_status)


def forward():
    global index
    print(index, len(prev))
    if index == len(prev) - 1:
        try:
            state, status = next(rocket)
        except StopIteration:
            pass
        else:
            index += 1
            display(state, **status)
            prev.append((state, status))
    else:
        index += 1
        state, status = prev[index]
        display(state, **status)


def backward():
    global index
    if index > 0:
        index -= 1
        state, status = prev[index]
        display(state, **status)


def forward50():
    for _ in range(50):
        forward()


def backward50():
    for _ in range(50):
        backward()


buttonForward = tk.Button(top, text="Forward", command=forward)
buttonBackward = tk.Button(top, text="Backward", command=backward)
buttonForward50 = tk.Button(top, text="Forward 50", command=forward50)
buttonBackward50 = tk.Button(top, text="Backward 50", command=backward50)

timeLabel.pack()
altLabel.pack()
velLabel.pack()
stateLabel.pack()
indexLabel.pack()
buttonForward.pack()
buttonBackward.pack()
buttonForward50.pack()
buttonBackward50.pack()
top.mainloop()