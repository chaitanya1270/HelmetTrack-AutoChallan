from Number_plate import number_plate
from Update_img import insert_data_into_mongodb
import tensorflow as tf
from time import sleep
import cv2 as cv
import argparse
import sys
import numpy as np
import os.path
from glob import glob
import pymongo
from pymongo import MongoClient
from sms import email_alert
from Email import get_email_for_bike_number
from e_challan import generate_challan
import pandas as pd


# Establish a connection to the MongoDB database
client = MongoClient("mongodb+srv://newuser:newuser123@cluster0.zwjwk35.mongodb.net/")
db = client["Helmet-detection"]
images_in_collection = db["images_in"]
without_helmet_collection = db["without-helmet"]

#from PIL import image
frame_count = 0             # used in mainloop  where we're extracting images., and then to drawPred( called by post process)
frame_count_out=0           # used in post process loop, to get the no of specified class value.
# Initialize the parameters
confThreshold = 0.5  #Confidence threshold
nmsThreshold = 0.4   #Non-maximum suppression threshold
inpWidth = 416       #Width of network's input image
inpHeight = 416      #Height of network's input image


# Load names of classes
classesFile = "obj.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "yolov3-obj.cfg"
modelWeights = "yolov3-obj_2400.weights"

net = cv.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i - 1] for i in net.getUnconnectedOutLayers()]


# Draw the predicted bounding box
def drawPred(classId, conf, left, top, right, bottom):

    global frame_count
# Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)
    label = '%.2f' % conf
    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    #Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    # print(label)            #testing
    #print(labelSize)        #testing
    #print(baseLine)         #testing

    label_name,label_conf = label.split(':')    #spliting into class & confidance. will compare it with person.
    if label_name == 'helmet':
        #will try to print of label have people.. or can put a counter to find the no of people occurance.
        #will try if it satisfy the condition otherwise, we won't print the boxes or leave it.
        cv.rectangle(frame, (left, top - round(1.5*labelSize[1])), (left + round(1.5*labelSize[0]), top + baseLine), (255, 255, 255), cv.FILLED)
        cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 1)
        frame_count+=1


    #print(frame_count)
    if(frame_count> 0):
        return frame_count




# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]
    global frame_count_out
    frame_count_out=0
    classIds = []
    confidences = []
    boxes = []
    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []               #have to fins which class have hieghest confidence........=====>>><<<<=======
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                #print(classIds)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    count_person=0 # for counting the classes in this loop.
    for i in indices:
        # i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        #this function in  loop is calling drawPred so, try pushing one test counter in parameter , so it can calculate it.
        frame_count_out = drawPred(classIds[i], confidences[i], left, top, left + width, top + height)
        #increase test counter till the loop end then print...

        #checking class, if it is a person or not

        my_class='helmet'                   #======================================== mycode .....
        unknown_class = classes[classId]

        if my_class == unknown_class:
            count_person += 1
    #if(frame_count_out > 0):
    # print(frame_count_out)


    if count_person >= 1:
        path = 'test_out/'
        frame_name=os.path.basename(fn)             # trimm the path and give file name.
        cv.imwrite(str(path)+frame_name, frame)     # writing to folder.
        #print(type(frame))
        # cv.imshow('img',frame)
        # cv.waitKey(2000)
    else:
        # print(frame)
        # path = 'test_out_res/'
        # frame_name=os.path.basename(fn)             # trimm the path and give file name.
        # cv.imwrite(str(path)+frame_name, frame)
        bike_num = ((number_plate(frame))[-10:]).upper()
        # cv.imshow('img',frame)
        # cv.waitKey(0)
        insert_data_into_mongodb(bike_num, frame)
        email1 = get_email_for_bike_number(bike_num)
        email_alert("E-Challan Alert - Helmet Violation","This is to inform you that an e-challan has been issued for a recent traffic violation. The violation pertains to not wearing a helmet while riding a vehicle. For your safety and to avoid further penalties, please verify this e-challan by visiting the official e-challan website. Ensure that you settle any fines or address the violation promptly.Official E-Challan Website: [Website URL] If you have any questions or require assistance, please contact our customer support team at [Contact Information]. Thank you for your cooperation in following traffic regulations. ",email1)

    #cv.imwrite(frame_name, frame)

# # Process inputs
# winName = 'Deep learning object detection in OpenCV'
# cv.namedWindow(winName, cv.WINDOW_NORMAL)
# Avoid OOM errors by setting GPU Memory Consumption Growth
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus: 
    tf.config.experimental.set_memory_growth(gpu, True)

# Update the file extensions to include .jpg, .jpeg, and .png
image_extensions = ['*.jpg', '*.jpeg', '*.png']

for extension in image_extensions:
    for fn in glob(f'images/{extension}'):
        frame = cv.imread(fn)
        frame_count =0

        # Create a 4D blob from a frame.
        blob = cv.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(getOutputsNames(net))

        # Remove the bounding boxes with low confidence
        postprocess(frame, outs)

        # Put efficiency information. The function getPerfProfile returns the overall time for inference(t) and the timings for each of the layers(in layersTimes)
        t, _ = net.getPerfProfile()
        #print(t)
        label = 'Inference time: %.2f ms' % (t * 1000.0 / cv.getTickFrequency())
        #print(label)
        cv.putText(frame, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        #print(label)