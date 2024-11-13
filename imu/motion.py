"""This file contains the base Class for motion functions"""


class BowlingPhysics:
    def __init__(self, ball_mass, friction, pin_mass):
        self.ball_mass = ball_mass
        self.friction = friction
        self.pin_mass = pin_mass

    def get_speed(self, acceleration, time_interval):
        return acceleration * time_interval

    def get_momentum(self, speed):
        return self.ball_mass * speed

    def apply_friction(self, speed, time_interval):
        return max(0, speed - self.friction * time_interval)


"""
Sample usage:
physics = BowlingPhysics()
speed = physics.get_speed(accel_data, time_interval)
"""
