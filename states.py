"""All the states as Java style static classes in line with rules

Originally written for when there is error involved."""


class State:
    """The base state class. States (for regionals) need just a condition
    method (pulled from the rules) as well as an update function that would
    have been used to update the filter."""

    def __init__(self, start_time, start_alt):
        self.last_time = start_time
        self.last_alt = start_alt
        self.last_vel = 0.0

    @classmethod
    def set_next_state(cls, scls):
        """Decorator for seamless next_state setting. Mostly for code
        readability. Without this we'd need to have the states in reverse
        order with only negligible one-time performance benefit."""
        cls.next_state = scls
        return scls

    @staticmethod
    def condition(times, alts, vels):
        """The condition for advancing to this state"""
        raise NotImplementedError

    def velocity(self, time, altitude):
        """Update the spline with the latest data.
        Returns (altitude, velocity). Would have been used w/ error
        correction w/ filter."""

        velocity = (altitude - self.last_alt)/(time - self.last_time)
        self.last_alt, self.last_time = altitude, time
        return velocity


class Launch(State):
    """The rocket begins in the Launch state (v>0ft/s)."""
    pass


@Launch.set_next_state
class Drogue(State):
    """To enter the Drogue state and safely deploy the drogue parachute, the
    rocket must ensure it is descending (v<0ft/s)or, in the case of barometer
    failure, a failsafe time has been reached (t>15s)"""

    @staticmethod
    def condition(times, alts, vels):
        return times[2] > 15 or all(vel < 0 for vel in vels)


@Drogue.set_next_state
class Main(State):
    """To enter the Main state and deploy the main parachute, the rocket must
    be low enough to ensure it doesn't drift too far (h<200ft)."""

    @staticmethod
    def condition(times, alts, vels):
        return all(alt < 200 for alt in alts)


@Main.set_next_state
class Landed(State):
    """To enter the Landed state and activate the recovery GPS, the rocket
    must be stationary on the ground (v=0ft/s).

    WARNING: state is impossible to reach with the sample xls data"""

    @staticmethod
    def condition(times, alts, vels):
        return all(vel < 1 for vel in vels)


InitialState = Launch  # Set initial state
