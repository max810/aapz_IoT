#!/home/max810/venv/main37/bin/python

import logging
import logging.handlers
import argparse
import signal
import subprocess
import sys
import os
import time
from bluetooth import *

P: subprocess.Popen = None


class LoggerHelper(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        pass


def setup_logging():
    # Default logging settings
    LOG_FILE = "bt_server.log"
    LOG_LEVEL = logging.INFO

    # Define and parse command line arguments
    argp = argparse.ArgumentParser(description="Raspberry PI Bluetooth Server")
    argp.add_argument("-l", "--log", help="log (default '" + LOG_FILE + "')")

    # Grab the log file from arguments
    args = argp.parse_args()
    if args.log:
        LOG_FILE = args.log

    # Setup the logger
    logger = logging.getLogger(__name__)
    # Set the log level
    logger.setLevel(LOG_LEVEL)
    # Make a rolling event log that resets at midnight and backs-up every 3 days
    handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        backupCount=3
    )

    # Log messages should include time stamp and log level
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)

    # Replace stdout with logging to file at INFO level
    sys.stdout = LoggerHelper(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = LoggerHelper(logger, logging.ERROR)


def stop_video_stream():
    global P
    if not P:
        return
    P.send_signal(signal.SIGINT)
    P = None


def start_video_stream():
    global P
    if P:
        return
    P = subprocess.Popen(["/home/max810/venv/main37/bin/python", "/home/max810/aapz_project/IoT.py"])  # /home/max810/aapz_project/


def main():
    # Setup logging
    setup_logging()

    # We need to wait until Bluetooth init is done
    time.sleep(10)

    # Make device visible
    os.system("hciconfig hci0 piscan")

    # Create a new server socket using RFCOMM protocol
    server_sock = BluetoothSocket(RFCOMM)
    # Bind to any port
    server_sock.bind(("", PORT_ANY))
    # Start listening
    server_sock.listen(1)

    # Get the port the server socket is listening
    port = server_sock.getsockname()[1]

    # The service UUID to advertise
    uuid = "7be1fcb3-5776-42fb-91fd-2ee7b5bbb86d"

    # Start advertising the service
    advertise_service(server_sock, "RaspiBtSrv",
                      service_id=uuid,
                      service_classes=[uuid, SERIAL_PORT_CLASS],
                      profiles=[SERIAL_PORT_PROFILE])

    # These are the operations the service supports
    # Feel free to add more
    # operations = ["ping", "example"]

    # Main Bluetooth server loop
    # This will block until we get a new connection
    print("Waiting for connection on RFCOMM channel %d" % port)
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    while True:
        try:
            data = client_sock.recv(1024).decode('utf-8')
            if len(data) == 0:
                break

            print("Received [%s]" % data)

            # Handle the request
            if data == "0":
                stop_video_stream()
                response = "msg:[-]Stopped stream"
            elif data == "1":
                start_video_stream()
                response = "msg:[+]Started stream"
            else:
                response = "msg:[.]Not supported"

            client_sock.send(response)
            print("Sent back [%s]" % response)

        except IOError:
            pass

        except KeyboardInterrupt:

            if client_sock is not None:
                client_sock.close()

            server_sock.close()

            print("Server going down")
            break


if __name__ == '__main__':
    main()
