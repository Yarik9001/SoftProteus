# import numpy as np
import cv2
import time 
cap = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 30.0, (640,480))

start = time.time()

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,1)
        #text
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = str(round(time.time() - start ,2))
        frame=cv2.putText(frame,text,(50,450), font, 1,(255,255,255),2,cv2.LINE_AA)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finishedq
cap.release()
out.release()
cv2.destroyAllWindows()
finish = time.time()
result = finish - start
print("Program time: " + str(result) + " seconds.")