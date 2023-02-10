import cv2
import pyautogui
import numpy as np
import socket
import pickle
import struct
import threading

class StreamingClient:

    def __init__(self, host, port):

        self.__host = host
        self.__port = port
        self._configure()
        self.__running = False
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _configure(self):

        self.__encoding_parameters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

    def _get_frame(self):

        return None

    def _cleanup(self):

        cv2.destroyAllWindows()

    def __client_streaming(self):

        self.__client_socket.connect((self.__host, self.__port))
        while self.__running:
            frame = self._get_frame()
            result, frame = cv2.imencode('.jpg', frame, self.__encoding_parameters)
            data = pickle.dumps(frame, 0)
            size = len(data)

            try:
                self.__client_socket.sendall(struct.pack('>L', size) + data)
            except ConnectionResetError:
                self.__running = False
            except ConnectionAbortedError:
                self.__running = False
            except BrokenPipeError:
                self.__running = False

        self._cleanup()

    def start_stream(self):
        """
        Starts client stream if it is not already running.
        """

        if self.__running:
            print("Client is already streaming!")
        else:
            self.__running = True
            client_thread = threading.Thread(target=self.__client_streaming)
            client_thread.start()

    def stop_stream(self):

        if self.__running:
            self.__running = False
        else:
            print("Client not streaming!")


class CameraClient(StreamingClient):


    def __init__(self, host, port, x_res=1024, y_res=576):

        self.__x_res = x_res
        self.__y_res = y_res
        self.__camera = cv2.VideoCapture(0)
        super(CameraClient, self).__init__(host, port)

    def _configure(self):

        self.__camera.set(3, self.__x_res)
        self.__camera.set(4, self.__y_res)
        super(CameraClient, self)._configure()

    def _get_frame(self):

        ret, frame = self.__camera.read()
        return frame

    def _cleanup(self):

        self.__camera.release()
        cv2.destroyAllWindows()


class VideoClient(StreamingClient):
    

    def __init__(self, host, port, video, loop=True):

        self.__video = cv2.VideoCapture(video)
        self.__loop = loop
        super(VideoClient, self).__init__(host, port)

    def _configure(self):

        self.__video.set(3, 1024)
        self.__video.set(4, 576)
        super(VideoClient, self)._configure()

    def _get_frame(self):

        ret, frame = self.__video.read()
        return frame

    def _cleanup(self):

        self.__video.release()
        cv2.destroyAllWindows()


class ScreenShareClient(StreamingClient):
    

    def __init__(self, host, port, x_res=1024, y_res=576):

        self.__x_res = x_res
        self.__y_res = y_res
        super(ScreenShareClient, self).__init__(host, port)

    def _get_frame(self):

        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_res, self.__y_res), interpolation=cv2.INTER_AREA)
        return frame

sender = ScreenShareClient('172.22.22.62', 9999)

t = threading.Thread(target=sender.start_stream)
t.start()

while input("") != 'stop':
    continue

sender.stop_stream()