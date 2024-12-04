
# Credit to https://github.com/Practical-CV/Simple-object-tracking-with-OpenCV
# USAGE
# python position_tracker.py --prototxt deploy.prototxt --model res10_300x300_ssd_iter_140000.caffemodel

# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from imutils.video import VideoStream
import numpy as np
import argparse
import imutils
import cv2
import socket, time
def connect_with_retry():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect(('localhost', 8081))
            print("camera connected to server")
            return client_socket
        except ConnectionRefusedError:
            print("Server not available, retrying in 1 second...")
            time.sleep(1)

client_socket = connect_with_retry()
print("Camera socket has been connected")

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
	help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.5,
	help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# initialize our centroid tracker and frame dimensions
ct = CentroidTracker()

(H, W) = (None, None)

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialize the video stream and allow the camera sensor to warmup
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

# calculate distance from center along x-axis
def calculate_x_axis_distance_from_center(centroid, frame_width):
    center_x = frame_width / 2
    distance_from_center = centroid[0] - center_x
    return distance_from_center

def is_valid_float(value):
    try:
        float(str(value))
        return True
    except:
        return False

# loop over the frames from the video stream
while True:
	# read the next frame from the video stream and resize it
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# if the frame dimensions are None, grab them
	if W is None or H is None:
		(H, W) = frame.shape[:2]

	# construct a blob from the frame, pass it through the network,
	# obtain our output predictions, and initialize the list of
	# bounding box rectangles
	blob = cv2.dnn.blobFromImage(frame, 1.0, (W, H),
		(104.0, 177.0, 123.0))
	net.setInput(blob)
	detections = net.forward()
	rects = []

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# filter out weak detections by ensuring the predicted
		# probability is greater than a minimum threshold
		if detections[0, 0, i, 2] > args["confidence"]:
			# compute the (x, y)-coordinates of the bounding box for
			# the object, then update the bounding box rectangles list
			box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
			rects.append(box.astype("int"))

			# draw a bounding box surrounding the object so we can
			# visualize it
			# (startX, startY, endX, endY) = box.astype("int")
			# cv2.rectangle(frame, (startX, startY), (endX, endY),
			# 	(0, 255, 0), 2)

	# update our centroid tracker using the computed set of bounding
	# box rectangles
	objects = ct.update(rects)

	# loop over the tracked objects
	for (objectID, centroid) in objects.items():

		distance = calculate_x_axis_distance_from_center(centroid, W)
		if is_valid_float(distance):
			try:
				client_socket.send(str(distance).encode())
			except socket.error:
				pass
		# print(f"distance: {distance}")

		# # draw both the ID of the object and the centroid of the
		# # object on the output frame
		# text = "ID {}".format(objectID)
		# cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
		# 	cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		# cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
		
	# # show the output frame
	# cv2.imshow("Frame", frame)
	# key = cv2.waitKey(1) & 0xFF

	# # if the `q` key was pressed, break from the loop
	# if key == ord("q"):
	# 	break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()