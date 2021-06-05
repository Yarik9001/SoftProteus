# import required libraries
from vidgear.gears import NetGear
import cv2

# define tweak flags
options = {"flag": 0, "copy": False, "track": False}

client = NetGear(
    address="192.168.1.102",
    port="5454",
    protocol="tcp",
    pattern=0,
    receive_mode=True,
    logging=True,
    **options
)

# loop over
while True:

    # receive frames from network
    frame = client.recv()

    # check for received frame if Nonetype
    if frame is None:
        break

    # {do something with the received frame here}

    # Show output window
    cv2.imshow("Output Frame", frame)

    # check for 'q' key if pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# close output window
cv2.destroyAllWindows()

# safely close client
client.close()