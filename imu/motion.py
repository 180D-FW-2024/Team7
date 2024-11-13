"""This file contains the base Class for motion functions"""

from utils.config import *


class BowlingPhysics:
    def __init__(self, ball_mass, friction, pin_mass):
        self.ball_mass = ball_mass
        self.friction = friction
        self.pin_mass = pin_mass

    def get_speed(self, acceleration, time_interval):
        pass

    def get_momentum(self, speed):
        pass

    def apply_friction(self, speed, time_interval):
        pass


"""
Sample usage:
physics = BowlingPhysics()
speed = physics.get_speed(accel_data, time_interval)
"""
