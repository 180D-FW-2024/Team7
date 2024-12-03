import cv2
from cvzone.SelfiSegmentationModule import SelfiSegmentation

# connecting the internal camera (first camera index will be 0, it is the default)
cap = cv2.VideoCapture(0)

# extracting the camera capture size
width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# loading and resizing the background image
background_image = cv2.resize(cv2.imread("bg_image.jpeg"), (width, height))
segmentor = SelfiSegmentation()
while True:
    # Reading the captured images from the camera
    ret, frame = cap.read()

    # segmenting the image
    segmentated_img = segmentor.removeBG(frame, background_image)

    # concatenating the images horizontally
    concatenated_img = cv2.hconcat([frame, segmentated_img])

    # Display the images
    cv2.imshow("Camera Live", concatenated_img)

    # ending condition
    if cv2.waitKey(1) == ord('q'):
        break

# releasing the sources


# what am i doing
print("making a change")
cap.release()
cv2.destroyAllWindows()
