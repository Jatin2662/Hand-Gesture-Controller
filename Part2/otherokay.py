import cv2
import numpy as np
import HandTrackingModule as htm
import autopy
import math
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk


wCam, hCam = 640, 480
frameR = 100  # Frame Reduction

class HandGestureApp:
    def __init__(self, root, cap):
        self.root = root
        self.root.title("Hand Gesture Control")
        self.cap = cap

        # Initialize variables
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.is_running = False
        self.smoothening_factor = 10  # Default smoothening factor

        # Set up GUI components
        self.root.configure(bg='#F0F0F0')  # Set background color
        self.canvas = tk.Canvas(root, width=wCam, height=hCam, bg='#F0F0F0')
        self.canvas.pack()

        # Start button
        self.start_button = tk.Button(root, text="Start", command=self.start, fg='#FFFFFF', bg='#4CAF50', padx=10)
        self.start_button.pack(side=tk.LEFT, padx=10)

        # Stop button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop, fg='#FFFFFF', bg='#FF0000', padx=10)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Smoothening slider
        self.smoothening_label = tk.Label(root, text="Smoothening", bg='#F0F0F0')
        self.smoothening_label.pack(side=tk.LEFT)
        self.smoothening_slider = ttk.Scale(root, from_=1, to=50, orient=tk.HORIZONTAL, command=self.set_smoothening, length=150)
        self.smoothening_slider.set(self.smoothening_factor)
        self.smoothening_slider.pack(side=tk.LEFT, padx=10)

        # Help button
        self.help_button = tk.Button(root, text="Help", command=self.show_help, fg='#FFFFFF', bg='#3498db', padx=10)
        self.help_button.pack(side=tk.LEFT, padx=10)

        # Exit button
        self.exit_button = tk.Button(root, text="Exit", command=self.quit, fg='#FFFFFF', bg='#333333', padx=10)
        self.exit_button.pack(side=tk.RIGHT, padx=10)

        # Help text
        self.help_text = """
        Possible Hand Movements:
        1. Right-click: Hold your index finger close to the thumb.
        2. Moving mode: Point your index finger, and move the cursor by moving your hand.
        3. Left-click: Close your index and middle fingers, then click.
        4. Volume control: Extend your index and pinky fingers, and adjust distance for volume control.
        """

        # Set up hand tracking module
        self.detector = htm.handDetector(maxHands=1)

        # Set up audio control
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]

        # Set up screen dimensions
        self.wScr, self.hScr = autopy.screen.size()

        # Run the Tkinter main loop
        self.root.after(10, self.update)

    def start(self):
        self.is_running = True

    def stop(self):
        self.is_running = False

    def set_smoothening(self, value):
        self.smoothening_factor = int(round(float(value)))

    def show_help(self):
        help_popup = tk.Toplevel(self.root)
        help_popup.title("Hand Gesture Control - Help")

        # Create scrolled text widget
        help_text_widget = scrolledtext.ScrolledText(help_popup, wrap=tk.WORD, width=50, height=20)
        help_text_widget.insert(tk.INSERT, self.help_text)
        help_text_widget.pack(expand=True, fill="both")

    def update(self):
        if self.is_running:
            success, img = self.cap.read()
            img = self.detector.findHands(img)
            lmList, bbox = self.detector.findPosition(img)

            if len(lmList) != 0:
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]
                x3, y3 = lmList[4][1], lmList[4][2]
                x4, y4 = lmList[8][1], lmList[8][2]
                cx, cy = (x3 + x4) // 2, (y3 + y4) // 2

                fingers = self.detector.fingersUp()

                length = math.hypot(x4 - x3, y4 - y3)

                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

                if length < 40 and fingers[3] == 0 and fingers[4] == 0 and fingers[2] == 0:
                    autopy.mouse.click(autopy.mouse.Button.RIGHT)

                if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0 and fingers[0] == 0:
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, self.wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, self.hScr))

                    self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening_factor
                    self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening_factor

                    autopy.mouse.move(self.wScr - self.clocX, self.clocY)
                    self.plocX, self.plocY = self.clocX, self.clocY

                if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0 and fingers[0] == 0:
                    length, img, lineinfo = self.detector.findDistance(8, 12, img)
                    if length < 40:
                        autopy.mouse.click()

                if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[0] == 1:
                    vol = np.interp(length, [60, 300], [self.minVol, self.maxVol])
                    self.volume.SetMasterVolumeLevel(vol, None)

            img = cv2.flip(img, 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)

            self.canvas.img = img
            self.canvas.create_image(5, 5, anchor=tk.NW, image=img)

        self.root.after(10, self.update)

    def quit(self):
        self.cap.release()
        self.root.destroy()

# Set up OpenCV capture
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

# Set up GUI
root = tk.Tk()
app = HandGestureApp(root, cap)

# Run the Tkinter main loop
root.mainloop()