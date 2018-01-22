"""Single-member module with Rocket class"""

from typing import Generator, Tuple
from random import uniform
from collections import deque

from csv import Error as csvError
from xlrd import XLRDError
import states
import readers

DataGen = Generator[Tuple[float, float], None, None]


class Rocket:
    """Simple iterator (previous history is left for the frontend to handle)"""

    last_time = -1
    last_three = deque(maxlen=3)

    def __init__(self, data_file: str, error: float = .001):
        self.error = error

        try:
            self.data = readers.read_csv(data_file)
            self.state = states.InitialState(*next(self.data), 0)
            return
        except (UnicodeDecodeError, csvError):
            pass

        try:
            self.data = readers.read_xls(data_file)
            self.state = states.InitialState(*next(self.data), 0)
        except (IndexError, XLRDError):
            raise ValueError("File {} is not a correctly formed CSV or XLS"
                             .format(data_file))

    def __iter__(self):
        return self

    def __next__(self) -> str:
        time, altitude = next(self.data)

        if time <= self.last_time:
            raise ValueError("Time must strictly increase.")
        self.last_time = time

        e_altitude = altitude * uniform(1-self.error, 1+self.error)

        interp_alt, interp_vel = self.state.update(time, e_altitude)
        self.last_three.append((time, interp_alt, interp_vel))

        if len(self.last_three) == 3 \
           and self.state.next_state.condition(*zip(*self.last_three)):
            for _ in range(3):
                self.last_three.pop()
            self.state = self.state.next_state(time, interp_alt, interp_vel)
        return f"{type(self.state).__name__} {altitude} {interp_alt} {interp_vel}"


if __name__ == '__main__':
    import sys
    for state in Rocket("/home/alchzh/Downloads/coding.csv"):
        print(state, file=sys.stderr)
