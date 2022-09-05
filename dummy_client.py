import animus_client as animus
import animus_utils as utils
import sys
import logging
import numpy as np
import random
import cv2
import time
import logging
import pygame
import os
import datetime
import os

from rollbody_utils import make_motor_cmd, send_speed_cmd, send_head_cmd


robot_name = "rollbody"

log = utils.create_logger("DebugClient", logging.INFO)
log.info(animus.version)


audio_params = utils.AudioParams(
            Backends=[""],
            SampleRate=16000,
            Channels=1,
            SizeInFrames=True,
            TransmitRate=30
        )

setup_result = animus.setup(audio_params, "Python3AnimusBasics", loglatency=True)
if not setup_result.success:
    sys.exit(-1)

# This will throw an error is system_login=True
email = os.environ["CYBERSELVES_EMAIL"]
pwd = os.environ["CYBERSELVES_PWD"]
log.info(f"CYBERSELVES email and pwd: {email}, {pwd}")
login_result = animus.login_user(email, pwd, system_login=False)       
if login_result.success:
    log.info("Logged in")
else:
    sys.exit(-1)

get_robots_result = animus.get_robots(True, True, get_system=False)
if not get_robots_result.localSearchError.success:
    log.error(get_robots_result.localSearchError.description)

if not get_robots_result.remoteSearchError.success:
    log.error(get_robots_result.remoteSearchError.description)

if len(get_robots_result.robots) == 0:
    log.info("No Robots found")
    animus.close_client_interface()
    sys.exit(-1)

for robot_details in get_robots_result.robots:
    if robot_details.name == robot_name:
        break
else:
    sys.exit(-1)

robot = animus.Robot(robot_details)

# Init all the communication channels
connected_result = robot.connect()
if not connected_result.success:
    log.error("Could not connect with robot {}".format(robot.robot_details.robot_id))
    animus.close_client_interface()
    sys.exit(-1)

# # ----------------Motor Loop------------------------------------

"""
open_success = robot.open_modality("motor")
if not open_success:
    log.error("Could not open robot motor modality")
    sys.exit(-1)

screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption('WindowToRegisterInputs')
screen.fill((234, 212, 252))
pygame.display.flip()

counter = 0
pygame.init()
clock = pygame.time.Clock()


while True:

    counter += 1
    clock.tick(20)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    pygame.event.pump() # update the keyboard state in memory
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        print('key left')
        send_speed_cmd(robot, 0, -1.)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        print('key right')
        send_speed_cmd(robot, 0, 1.)
    elif keys[pygame.K_UP] or keys[pygame.K_w]:
        print('key up')
        send_speed_cmd(robot, 1., 0)
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        send_speed_cmd(robot, -1., 0)
        print('key down')
    elif keys[pygame.K_u]:
        send_head_cmd(robot, 1.)
        print('key u')
    elif keys[pygame.K_p]:
        send_head_cmd(robot, -1.)
        print('key p')
    else:
        send_speed_cmd(robot, 0., 0.)
"""


# ----------------Motor Visual Loop------------------------------------

# Open modalities
open_success = robot.open_modality("vision")
if not open_success:
    log.error("Could not open robot vision modality")
    sys.exit(-1)

open_success = robot.open_modality("motor")
if not open_success:
    log.error("Could not open robot motor modality")
    sys.exit(-1)

open_success = robot.open_modality("proprioception")
if not open_success:
    log.error("Could not open robot proprioception modality")
    sys.exit(-1)

# screen = pygame.display.set_mode((300, 300))
# pygame.display.set_caption('WindowToRegisterInputs')
# screen.fill((234, 212, 252))
# pygame.display.flip()

motion_counter = 0
counter = 0
pygame.init()
clock = pygame.time.Clock()

compr_factor = 1
n = 0


try:
    while True:
        n += 1

        # PROPRIOCEPTION
        try:
            arr, err = robot.get_modality("proprioception")
            if err.success:
                compr_factor = arr[1]
            #print(arr)
        except Exception as e:
            print("SOME PROPRIOCEPTION ISSUE", e)
            continue

        # VISION
        try:
            # the backend receives YUV and automatically converts to BRG
            image_list, err = robot.get_modality("vision", True)    # returns a list object
        except Exception as e:
            print("SOME VISION ISSUE", e)
            continue
        if err.success:
            # cv2.cvtColor(myim, cv2.COLOR_RGB2BGR, myim)

            print("shapes")
            for img in image_list:
                print(img.image.shape)
            
            try:
                if len(image_list) in [1, 2]:
                    cv2.imshow("LeftCam", image_list[0].image)
                    cv2.imwrite(f"imgs/{n}.jpg", image_list[0].image)
                elif len(image_list) in [9, 18]:
                    # undo patch compr
                    resize = lambda x: cv2.resize(x, (int(x.shape[1]*compr_factor), int(x.shape[0]*compr_factor)))    # W,H
                    # stack horizontally
                    img_above_fov = resize(image_list[1].image)
                    row1 = np.concatenate((resize(image_list[0].image), 
                                            img_above_fov,
                                            resize(image_list[2].image)), axis=1)
                    img_left_fov = resize(image_list[3].image)
                    fov = image_list[4].image[:img_left_fov.shape[0], :img_above_fov.shape[1], :]
                    print(img_above_fov.shape, img_left_fov.shape, fov.shape)
                    row2 = np.concatenate((img_left_fov, 
                                            fov,
                                            resize(image_list[5].image)), axis=1)
                    row3 = np.concatenate((resize(image_list[6].image), 
                                            resize(image_list[7].image),
                                            resize(image_list[8].image)), axis=1)
                    # stack vertically
                    img = np.concatenate((row1, row2, row3), axis=0)

                    cv2.imshow("Patch Compressed", img)
                
                j = cv2.waitKey(1)
                if j == 27:
                    break
            except Exception as e:
                print(e)
                
        # MOTOR
        clock.tick(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.event.pump() # update the keyboard state in memory
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            print('key left')
            send_speed_cmd(robot, 0, -1.)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            print('key right')
            send_speed_cmd(robot, 0, 1.)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            print('key up')
            send_speed_cmd(robot, 1., 0)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            send_speed_cmd(robot, -1., 0)
            print('key down')
        elif keys[pygame.K_u]:
            send_head_cmd(robot, 1.)
            print('key u')
        elif keys[pygame.K_p]:
            send_head_cmd(robot, -1.)
            print('key p')
        else:
            send_speed_cmd(robot, 0., 0.)

except KeyboardInterrupt:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True
except SystemExit:
    cv2.destroyAllWindows()
    log.info("Closing down")
    stopFlag = True

cv2.destroyAllWindows()
if stopFlag:
    # Disconnect from robot
    robot.disconnect()

    # Close client interface
    animus.close_client_interface()
    sys.exit(-1)