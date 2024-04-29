import cv2
import time
import os
import HandTrackingModule as htm

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
folderpath = "fingercounting"
myList = os.listdir(folderpath)
print(myList)
overlayList = []
for impath in myList:
    image = cv2.imread(f'{folderpath}/{impath}')
    print(f'{folderpath}/{impath}')
    overlayList.append(image)
print(len(overlayList))
ctime = 0
ptime = 0

detector = htm.handDetector(detectionCon=0.75)

tipids = [4, 8, 12, 16, 20]

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList, _ = detector.findPosition(img, draw=False)
    print(lmList)
    if len(lmList) != 0:
        # if len(lmList) >= max(tipids):
            fingers = []
            # Thumb
            if lmList[tipids[0]][1] > lmList[tipids[0] - 1][1]:
                print("Index finger open")
                fingers.append(1)
            else:
                fingers.append(0)
            # 4 Fingers
            for id in range(1, 5):
                if lmList[tipids[id]][2] < lmList[tipids[id] - 2][2]:
                    print("Index finger open")
                    fingers.append(1)
                else:
                    fingers.append(0)

            print(fingers)
            totalfingers = fingers.count(1)
            print(totalfingers)
            h, w, c = overlayList[totalfingers - 1].shape
            img[0:h, 0:w] = overlayList[totalfingers - 1]

            cv2.rectangle(img, (20, 225), (170, 425), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(totalfingers), (45, 375), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 25)

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, f'FPS:{str(int(fps))}', (400, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)