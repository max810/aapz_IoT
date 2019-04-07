import cv2
# TODO : think about another Thread
import socket
import requests

RECEIVER_IP = "192.168.31.62"
RECEIVER_PORT = -1
VIDEO_FILE_PATH = "video_ready_5.mp4"
ENCODE_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), 40]


def start_video_stream(sock):
    cap = cv2.VideoCapture(VIDEO_FILE_PATH)
    i = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
                continue
            frame = cv2.resize(frame, (266, 200))
            data_str = cv2.imencode('.jpg', frame, ENCODE_PARAMS)[1].tobytes()
            sock.sendto(data_str, (RECEIVER_IP, RECEIVER_PORT))

            i += 1

            if i % 30 == 0:
                print("Sent ", i, " packets")
    finally:
        sock.close()


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Recovering stream...")
    res = requests.post("http://{}:{}/api/Stream/start-stream".format(RECEIVER_IP, 5000), params={
        'driverIdentifier': "1"
    }, timeout=60000)

    print("type(res.status_code) = ", type(res.status_code))
    status = int(res.status_code)
    if status == 200:
        print("Stream started!")
        RECEIVER_PORT = int(res.content)
        print("Sending to port ", RECEIVER_PORT)
        start_video_stream(sock)
    else:
        print("received: {}".format(res.content))
        print("code: {}".format(status))
        exit(1)
