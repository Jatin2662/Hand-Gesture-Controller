import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

###########################################

wCam, hCam = 640, 480

###########################################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
ptime = 0
ctime = 0

detector = htm.handDetector(detectionCon=0.7,maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorvol=(255,0,0)

while True:
    success, img = cap.read()

    # Find hands
    # filter based on size
    # find distance between index and thumb
    # convet volume
    # reduce resolution to make it smoother
    # check fingers up
    # if pinky is down set volume
    # drawings
    # framerates

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        # print(bbox)
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(area)
        if 250 < area < 1000:
            # print("yes")

            length, img, lineinfo = detector.findDistance(4, 8, img)
            # print(length)
            # print(length)

            # Hand range 40 - 300
            # Volume Range -63.5 - 0
            # vol = np.interp(length, [40, 300], [minVol, maxVol])

            volBar = np.interp(length, [40, 200], [400, 150])
            volPer = np.interp(length, [40, 200], [0, 100])
            # print(int(length), vol)
            # volume.SetMasterVolumeLevel(vol, None)


            smoothness = 5
            volPer = smoothness * round(volPer / smoothness)

            fingers=detector.fingersUp()
            # print(fingers)

            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 7, (0, 255, 0), cv2.FILLED)
                colorvol=(0,255,0)
                # time.sleep(0.25)
            else:
                colorvol=(255,0,0)




    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} ', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)

    cv2.putText(img, f'Vol Set: {int (cVol)} ', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorvol, 3)




    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, f'FPS: {(int(fps))}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
         break