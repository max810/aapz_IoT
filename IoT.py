import cv2
# TODO : think about another Thread
import socket

UDP_IP = "192.168.31.62"
UDP_PORT = 5005
MAX_NUM_CONNECTIONS = 20
VIDEO_FILE_PATH = "video_ready_5.mp4"
ENCODE_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), 40]

if __name__ == '__main__':
    cap = cv2.VideoCapture(VIDEO_FILE_PATH)
    print("Waiting connections...")
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
                continue
            frame = cv2.resize(frame, (266, 200))
            data_str = cv2.imencode('.jpg', frame, ENCODE_PARAMS)[1].tobytes()
            connection.sendto(data_str, (UDP_IP, UDP_PORT))
    finally:
        connection.close()
