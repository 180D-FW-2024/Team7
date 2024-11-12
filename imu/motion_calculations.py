from utils.constants import RAD_TO_DEG, G_GAIN, AA, BALL_MASS, FRICTION, PIN_MASS

"""This file contains the base Class for motion functions"""


class BowlingPhysics:
    def __init__(self, ball_mass=BALL_MASS, friction=FRICTION, pin_mass=PIN_MASS):
        self.ball_mass = ball_mass
        self.friction = friction
        self.pin_mass = pin_mass

    def get_speed(accel_data, delta_time):
        """Calculate speed from accelerometer data"""
        pass

    def get_angle(accel_data, gyro_rate, delta_time):
        """Calculate throw angle from accelerometer data"""
        pass

    def get_spin(gyro_data):
        """Calculate spin rate from gyroscope data"""
        pass

    def get_momentum(mass, speed):
        """Calculate momentum using mass and speed"""
        pass

    def apply_friction(speed, friction_coefficient, delta_time):
        """Apply friction to reduce speed over time"""
        pass

    def get_collision_impact(momentum, spin, pin_mass, elasticity):
        """Calculate the impact force on collision with pins"""
        pass

    def get_angular_momentum(spin_rate):
        """Calculate the angular momentum based on spin rate"""
        pass


"""
Sample usage:
physics = BowlingPhysics()
speed = physics.get_speed(accel_data, time_interval)
"""
