"""All the states as Java style static classes in line with rules"""

from typing import Tuple, List
from scipy.interpolate import UnivariateSpline


FTriplet = Tuple[float, float, float]  # Tuple with three floats


class State:
    """The base state class. States (for regionals) need just a condition
    method (pulled from the rules) as well as an update function to update
    the spline"""

    smoothing: int = None  # Not no smoothing, this is scipy default smoothing!
    next_state: 'State' = None

    def __init__(self, start_time: float, start_alt: float,
                 start_vel: float) -> None:
        self.times: List[float] = [start_time]
        self.alts: List[float] = [start_alt]
        self.interp_alts: List[float] = [start_alt]
        self.interp_vels: List[float] = [start_vel]

    @classmethod
    def set_next_state(cls, scls: 'State'):
        """Decorator for seamless next_state setting. Mostly for code
        readability. Without this we'd need to have the states in reverse
        order with only negligible one-time performance benefit."""
        cls.next_state = scls
        return scls

    @staticmethod
    def condition(times: FTriplet, alts: FTriplet, vels: FTriplet) -> bool:
        # pylint: disable=W0613
        """The condition for advancing to this state"""
        raise NotImplementedError

    def update(self, time: float, altitude: float) -> Tuple[float, float]:
        """Update the spline with the latest data.
        Returns (altitude, velocity)"""

        self.times.append(time)
        self.alts.append(altitude)

        if len(self.times) >= 4:
            spl = UnivariateSpline(self.times, self.alts, s=self.smoothing)
            interp_alt = spl(time, 0)
            interp_vel = spl(time, 1)
        else:
            interp_alt = altitude
            interp_vel = (altitude-self.alts[-2])/(time-self.times[-2])

        self.interp_alts.append(interp_alt)
        self.interp_vels.append(interp_vel)

        return (interp_alt, interp_vel)


class Launch(State):
    """The rocket begins in the Launch state (v>0ft/s)."""
    pass


@Launch.set_next_state
class Drogue(State):
    """To enter the Drogue state and safely deploy the drogue parachute, the
    rocket must ensure it is descending (v<0ft/s)or, in the case of barometer
    failure, a failsafe time has been reached (t>15s)"""

    @staticmethod
    def condition(times: FTriplet, alts: FTriplet, vels: FTriplet) -> bool:
        return times[2] > 15 or all(vel < 0 for vel in vels)


@Drogue.set_next_state
class Main(State):
    """To enter the Main state and deploy the main parachute, the rocket must
    be low enough to ensure it doesn’t drift too far (h<200ft)."""
    @staticmethod
    def condition(times: FTriplet, alts: FTriplet, vels: FTriplet) -> bool:
        return all(i < 200 for i in alts)


@Main.set_next_state
class Landed(State):
    """To enter the Landed state and activate the recovery GPS, the rocket
    must be stationary on the ground (v=0ft/s).

    WARNING: This state is impossible to reach with the sample data"""

    @staticmethod
    def condition(times: FTriplet, alts: FTriplet, vels: FTriplet) -> bool:
        return False


InitialState = Launch  # Set initial state
