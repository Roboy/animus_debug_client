import numpy as np


def make_motor_cmd(lin_vel, ang_vel):
    return np.linspace(0, 1, 27).tolist() + [float(ang_vel), float(lin_vel)]


def send_motor_cmd(robot, lin_vel, ang_vel):
    return robot.set_modality("motor", make_motor_cmd(lin_vel, ang_vel))