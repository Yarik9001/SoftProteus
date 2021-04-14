import cv2
from time import  sleep

capture  = cv2.VideoCapture(0)

while True:
    ret, im = capture.read()
    cv2.imshow("From Camera", im)
    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break
    else:
        print(k)
    # sleep(1)

capture.release()
cv2.destroyAllWindows()