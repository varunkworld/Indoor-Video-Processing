# USAGE
# python path_tracking_v1.py --video example.mp4
# python path_tracking_v1.py

# import the necessary packages
from collections import deque
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import imutils
import cv2
from math import sqrt
import random
from nms import non_max_suppression_fast

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")

args = vars(ap.parse_args())

path = {}	# deque storing path of humans
color = {}	# color of path
check = {}	# number of points in path

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
	camera = cv2.VideoCapture(0)

# otherwise, grab a reference to the video file
else:
	camera = cv2.VideoCapture(args["video"])

old_circles = []

# keep looping
while True:
	# grab the current frame
	(grabbed, frame) = camera.read();

	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
	if args.get("video") and not grabbed:
		break

	frame = imutils.resize(frame, width=600)

	# detect people in the frame
	(rects, weights) = hog.detectMultiScale(frame, winStride=(4	, 4), padding=(8, 8), scale=1.05)
	rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
	pick = non_max_suppression_fast(rects, overlapThresh=0.65)

	# connecting new points to old paths
	if old_circles :
		for (xC,yC) in old_circles :
			flag = False
			for (xA, yA, xB, yB) in pick:
				(A,B) = ((xA+xB)/2, (yA+yB)/2)
				if( sqrt( (A - xC)**2 + (B - yC)**2 ) <= 50) :
					flag = True
					path[(A,B)] = path[(xC,yC)]
					color[(A,B)] = color[(xC,yC)]
					check[(A,B)] = check[(xC,yC)]
					if (A,B) != (xC,yC) :
						del color[(xC,yC)]
						del path[(xC,yC)]
						del check[(xC,yC)]
			if not flag and len(path[xC,yC]) < 10 :
				del path[(xC,yC)]
				del color[(xC,yC)]
				del check[(xC,yC)]

	old_circles = []
    # appending new points to paths
	for (xA, yA, xB, yB) in pick:
		cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
		(A,B) = ((xA+xB)/2, (yA+yB)/2)
		cv2.circle(frame, (A,B), 1, (0, 0, 255), -1)
		old_circles.append((A,B))
		if (A,B) not in path :
			print (str((A,B))+" not in path")
			color[(A,B)] = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
			check[(A,B)] = 0
			path[(A,B)] = deque()
		path[(A,B)].appendleft(((xA+xB)/2,yB))
		check[(A,B)] = check[(A,B)] + 1

	# printing paths
	for k in path :
		print ("person - "+str(k)+", path size (px) - " + str(len(path[k])) )
		pt = deque()
		if check[k] == 20 :
			pt.append(path[k][0])
			pt.append(path[k][19])
			for i in np.arange(20, len(path[k])):
				pt.append(path[k][i])
			path[k] = pt
			check[k] = 0
		for i in np.arange(1, len(path[k])):
			cv2.line(frame, path[k][i - 1], path[k][i], color[k], 2)

	print("---- next frame ----")
	cv2.imshow("Human Tracking",frame)
	key = cv2.waitKey(1) & 0xFF
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()