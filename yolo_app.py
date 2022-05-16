#!/usr/bin/python3

"""
Flask WebApp to access and control Raspberry Pi Rover with YOLO V5 object detection.

Author: Yash Indane
Email: yashindane46@gmail.com
"""

import torch
import cv2
import time
import argparse
import numpy as np
from PIL import Image
from subprocess import getoutput
from flask import Flask, Response, render_template, request


#Weigths and config for all models at https://pjreddie.com/darknet/yolo/

#Load model
model = torch.hub.load("ultralytics/yolov5", "yolov5s")

app = Flask("Raspberry Pi Rover")

#Open system Camera
cap = cv2.VideoCapture(0)

#For IP Webcam
#address = "https://<IP>:8080/video"
#cap.open(address)

#Counter for saving snaps
i = 0

#Flag to start pedestrian detection
detection_enable = False


#Changing value of detection flag
@app.route("/detection", methods=["GET"])
def enable_detection():
    global detection_enable
    if request.args.get("value") == "true":
        detection_enable = True
    else:
        detection_enable = False
    return "0"


#Detects Objects in frame using YOLO V5
def object_detection(frame):
    model(frame).save(save_dir="./")
    return np.asarray(Image.open(("image0.jpg")))
    #return cv2.imread("image0.jpg")

#Generating frames from stream
def gen():
    global final_frame
    prev_timestamp = 0
    while True:
        ret, frame = cap.read()
        initial_timestamp = time.time()
        #Processing frames
        try:
          scale_percent = 80
          width = int(frame.shape[1] * scale_percent/100)
          height = int(frame.shape[0] * scale_percent/100)
          dim = (width, height)
          frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
          if detection_enable:
              frame = object_detection(frame)
          FPS = "FPS " + str(int(1/(initial_timestamp-prev_timestamp)))
          prev_timestamp = initial_timestamp
          cv2.putText(frame, FPS, (7, 36), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,255,0), 2,  cv2.LINE_AA)
          ret, png = cv2.imencode(".jpg", frame)
          final_frame = frame
          frame = png.tobytes()
          yield(b'--frame\r\n'
               b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n\r\n')
        except Exception as e:
            print(e)


#For taking snaps
@app.route("/snap")
def snap():
    global i
    i += 1
    path = f"./snaps/image{str(i)}.png"
    cv2.imwrite(path, final_frame)
    return "0"


#For running commands
@app.route("/command", methods=["GET"])
def run_command():
    cmd = request.args.get("cmd")
    #Run the command
    command_status = getoutput(f"sudo {cmd}")
    return command_status


#This route is just streaming frames at a endpoint
#To use at other route <img src="http://<IP>:5500/stream" />
@app.route("/stream")
def stream():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


#Homepage
@app.route("/rover")
def rover():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5500")
