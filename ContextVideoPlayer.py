# -------------------------------------------------------------------------------
# Name:        ContextVideoPlayer
# Purpose:     UI To play video Files
#
# Author:      au.haque
#
# Created:     03-03-2015
# Copyright:   (c) au.haque 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy
import Tkinter as tk
from Tkinter import *
import ttk
import tkFileDialog
import cv2
import os
import GetInfo
from PIL import Image, ImageTk, ImageDraw
import threading


frame = None

lock = threading.Lock()


class Globals:
    Processing = False
    Stopped = True
    Vid = None
    Paused = False


class myThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):


        #try:

        setinfoText("Processing")
        img = processImage('zee.jpg')
        if img is not None:
            lmain.config(image=img)
            lmain.image = img
        if (infoText.text == 'Processing'):
            setinfoText(' ')
        #except Exception as ex:
         #   print "Exception Occured in processing Thread", ex.message



def processImage( path):
    persons = GetInfo.getInfoFromImage(os.path.abspath(path))
    txt = ""
    if persons is None:
        print 'no persons found'
        return None
    for person in persons:
        txt += 'Gender: ' + person['Gender'] + '\n'
        #txt += 'Age: ' + person['Age'] +'\n'

        if (person.has_key('Name')):
            txt += 'Name: ' + person['Name'] + '\n'
            txt += 'Recognitions: ' + '\n'
            for p in person['Professions']:
                txt += p + ', '
            txt += '\n'
            txt += 'More Info: ' + person['Info'] + '\n'
        txt += '\n'

    #print txt

    setinfoText(txt)

    boxParams = []
    #   boxParams = results[]
    for person in persons:
        boxP = [a for a in person['Size']]
        boxP.extend([a for a in person['Position']])
        boxParams.append(boxP)

    with lock:
        img = Image.open(path)
    draw = ImageDraw.Draw(img)
    for box in boxParams:
        draw.rectangle([(box[2], box[3]), (box[2] + box[0], box[3] + box[1])])

    img = ImageTk.PhotoImage(img)
    return img


def setinfoText(txt):
    infoText.text = txt
    infoText.delete(0.0, END)
    infoText.insert(0.0, txt)


imgProcessThread = None


def show_frame():
    global imgProcessThread
    if (not Globals.Stopped):
        if (not Globals.Paused):
            Globals.Processing = False
            global frame
            if ( Globals.Vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) - Globals.Vid.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) ) < 3:
                Globals.Stopped = True

            _, frame = Globals.Vid.read()
            #frame = cv2.flip(frame, 1)

            frameSize = (
            int(Globals.Vid.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)), int(Globals.Vid.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)))
            #sliderValue = int(Globals.cap.get(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO) *100)
            try:
                sliderValue = 100 * Globals.Vid.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) / Globals.Vid.get(
                    cv2.cv.CV_CAP_PROP_FRAME_COUNT)
            except Exception as ex:
                lmain.after(100, show_frame)
                return
            s.set(sliderValue)

            if (frameSize[1] > 480.0):
                ratio = frameSize[0] * 1.0 / frameSize[1]
                reduction = 480.0 / frameSize[1]
                frameSize = int(frameSize[1] * ratio * reduction), int(frameSize[1] * reduction)

            frame = cv2.resize(frame, frameSize)
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            img = Image.fromarray(cv2image)
            img = ImageTk.PhotoImage(image=img)

            lmain.image = img
            lmain.configure(image=img)
        else:
            if (not Globals.Processing):
                Globals.Processing = True
                with lock:
                    cv2.imwrite('zee.jpg', frame)
                if imgProcessThread is None:
                    imgProcessThread = myThread()
                    imgProcessThread.start()
                elif not imgProcessThread.is_alive():
                    imgProcessThread = myThread()
                    imgProcessThread.start()

        lmain.after(10, show_frame)
    else:
        lmain.after(100, show_frame)


def openFile():
    try:
        paths.set(open.show())
        if (Globals.Vid != None):
            Globals.Vid.release()
        Globals.Vid = cv2.VideoCapture(paths.get())

        root.titletext = "Context Based Image Search:SRBD - " + paths.get()
        root.title(root.titletext)
        Globals.Stopped = False
    except Exception as detail:
        print detail
        pass
    pass


def pause(event):
    Globals.Paused = not Globals.Paused
    print Globals.Paused


def play():
    pass


prevValue = 0.0


def setFrame(value):
    global prevValue
    value = float(value)
    if Globals.Vid != None and abs(prevValue - value) > 1:
        Globals.Vid.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, value * Globals.Vid.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT) / 100.0)
    prevValue = value


root = tk.Tk()

paths = StringVar()
root.resizable(width=False, height=False)
root.bind('<Escape>', lambda e: root.destroy())
root.bind('<space>', pause)
lmain = ttk.Label(root)
lmain.grid(row=0, column=0, columnspan=3, rowspan=1, sticky=(N, S, E, W))

s = ttk.Scale(root, orient=HORIZONTAL, from_=1.0, to=100.0, command=setFrame)
s.grid(row=1, column=0, columnspan=3, rowspan=3, sticky=(N, S, E, W))

infoPanel = Frame(root, width=100, padx=10, pady=5)
infoPanel.grid(column=3, row=0, sticky=(N, S, E, W))
infoText = Text(infoPanel, width=40, wrap='word', font='Arial 12 normal')
infoText.grid(column=0, row=0, sticky=(N, S, E, W))

myfiletypes = [('All files', '*')]
open = tkFileDialog.Open(root, filetypes=myfiletypes)
btn = Button(root, text="Open", command=openFile)
btn.grid(column=3, row=1, sticky=(W, E))

show_frame()
root.mainloop()