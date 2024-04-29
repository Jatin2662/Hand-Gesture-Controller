import os

import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720
folderpath ="C:\\Users\\kanch\\Desktop\\Nitish_ne_bhejya\\presentation_project\\ppt"
# camera setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# get the list of presentation images
pathimages = sorted(os.listdir((folderpath)),
                    key=len)  # as if we have number 10 image then it will come after 1 so to sort it we use sorted with key len

print(pathimages)

# variables
imgnumber = 0
hs, ws = int(120 * 1), int(213 * 1)
gesturethreshold = 300
buttonpressed = False
buttoncounter = 0
buttonDelay = 10
annotations = [[]]
annotationNumber = 0
annotationStart = False

# hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # importing images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathfullumage = os.path.join(folderpath, pathimages[imgnumber])
    imgcurrent = cv2.imread(pathfullumage)

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gesturethreshold), (width, gesturethreshold), (0, 255, 0), 10)
    if hands and buttonpressed == False:

        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']

        lmList = hand['lmList']

        # Constrain values for easier drawing
        xval = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yval = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))

        indexfinger = xval, yval

        # print(fingers)

        if cy <= gesturethreshold:  # if hand is at the height of the face
            annotationStart = False
            # gesture 1 -Left
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                annotationStart = False
                if imgnumber > 0:
                    buttonpressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgnumber -= 1

            # gesture 2 -Right
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                annotationStart = False
                if imgnumber < len(pathimages) - 1:
                    buttonpressed = True
                    annotations = [[]]
                    annotationNumber = 0
                    imgnumber += 1

        # gesture 3 - show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgcurrent, indexfinger, 12, (0, 0, 255), cv2.FILLED)
            annotationStart = False
        # gesture 4 - draw pointer
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgcurrent, indexfinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexfinger)
        else:
            annotationStart = False

        # gesture 5 - Erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonpressed = True
    else:
        annotationStart = False
    # button pressed iteration
    if buttonpressed:
        buttoncounter += 1
        if buttoncounter > buttonDelay:
            buttoncounter = 0
            buttonpressed = False

    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgcurrent, annotations[i][j - 1], annotations[i][j], (0, 0, 200), 12)

    # adding webcam image on the slide
    imgsmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgcurrent.shape
    imgcurrent[0:hs, w - ws:w] = imgsmall
    cv2.imshow("Image", img)
    cv2.imshow("Slides", imgcurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break