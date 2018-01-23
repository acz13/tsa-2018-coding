"""Single-member module with Rocket class

Called like this from command line:
python3 rocket.py DATA.csv
"""

from collections import deque
import os

from csv import Error as csvError
import states
import readers


class Rocket:
    """Simple iterator (previous history is left for the frontend to handle)"""

    last_three = deque(maxlen=3)

    def __init__(self, data_file):
        try:
            self.data = readers.read_csv(data_file)
            self.state = states.InitialState(*next(self.data))
            self.state_name = states.InitialState.__name__
            return
        except (UnicodeDecodeError, csvError):
            raise ValueError("File {} is not a correctly formed CSV"
                    .format(data_file))

    def __iter__(self):
        return self

    def __next__(self):
        time, altitude = next(self.data)

        if time <= self.state.last_time:
            raise ValueError("Time must strictly increase.")

        velocity = self.state.velocity(time, altitude)
        self.last_three.append((time, altitude, velocity))
        if len(self.last_three) == 3 \
           and hasattr(self.state, 'next_state') \
           and self.state.next_state.condition(*zip(*self.last_three)):
            for _ in range(3):
                self.last_three.pop()

            self.state_name = self.state.next_state.__name__
            self.state = self.state.next_state(time, altitude)

        return (self.state_name,
                {
                    'time': time,
                    'altitude': altitude,
                    'velocity': velocity
                }
               )
    
    next = __next__ # Python2


if __name__ == '__main__':
    from sys import argv

    last_state = None
    for state, status in Rocket(os.getcwd() + "/" + argv[1]):
        if state != last_state:
            print("Switching to {} state".format(state))
            last_state = state
        print("Time: {time:.3f}; Altitude: {altitude:.3f}; Velocity: {velocity:.3f};"
                .format(**status))
