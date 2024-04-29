import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

cap = cv2.VideoCapture(0)

##############################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 10
##############################

plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap.set(3, wCam)
cap.set(4, hCam)
ptime = 0
ctime = 0
detector = htm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        x3, y3 = lmList[4][1], lmList[4][2]
        x4, y4 = lmList[8][1], lmList[8][2]
        cx, cy = (x3 + x4) // 2, (y3 + y4) // 2
        # print(x1, y1, x2, y2)

        # 3. check which finger are up
        fingers = detector.fingersUp()
        # print(fingers)
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 7, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x4, y4), 7, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (x3, y3), (x4, y4), (255, 255, 0), 3)
        length = math.hypot(x4 - x3, y4 - y3)

        # Right-clicking
        if length < 40:
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED)
            autopy.mouse.click(autopy.mouse.Button.RIGHT)
        # 4. only index Finger: Moving mode
        if fingers[1] == 1 and fingers[2] == 0:
            # 5. convert coordinates

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. smoothen Values

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
        # 8. Both index and finger are up: clicking mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find th distanqce between fingers
            length, img, lineinfo = detector.findDistance(8, 12, img)
            # print(length)
            # 10.Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
        if fingers[1] == 1 and fingers[4] == 1 :
            vol = np.interp(length, [60, 300], [minVol, maxVol])
            # print(int(length), vol)
            volume.SetMasterVolumeLevel(vol, None)
            # while fingers[4] == 1 and fingers[1] == 1:
            # volume.SetMasterVolumeLevelScalar(volPer / 100, None)
            # print("controling volume")

        # 11.Frame Rate
    img = cv2.flip(img, 1)
    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime
    cv2.putText(img, f'FPS: {(int(fps))}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break