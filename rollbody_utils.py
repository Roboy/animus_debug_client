import numpy as np
import datetime


def make_motor_cmd(lin_vel, ang_vel):
    motor_cmd = [0.] * 8
    dtn = datetime.datetime.utcnow()
    motor_cmd[0] = dtn.hour + dtn.minute/60 + dtn.second/3600
    motor_cmd[1] = float(ang_vel)
    motor_cmd[2] = float(lin_vel)
    
    return motor_cmd


def send_motor_cmd(robot, lin_vel, ang_vel):
    return robot.set_modality("motor", make_motor_cmd(lin_vel, ang_vel))