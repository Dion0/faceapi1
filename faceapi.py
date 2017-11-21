import argparse
from scipy.misc import imsave
import cognitive_face as CF
import cv2, threading, time
from sys import platform
from time import sleep
from scipy.misc import imread

width = 0
top = 0
height = 0
left = 0
gender = 0
age = 0
rgbf = 0
flag = 0; ad_playing = False

class Cam(threading.Thread):
    def __init__(self, box_mutex):
        self.mutex = box_mutex
        self.running = False

        threading.Thread.__init__(self)

    def run(self):
        self.running = True
        global rgbf, width, top, height, left, gender, age, flag
        while self.running:
            sleep(0.51)
            imsave('tmp.png', rgbf)
            result = CF.face.detect('tmp.png', attributes='age,gender')
            with self.mutex:
                flag = 0
                width = 0
                top = 0
                left = 0
                height = 0
                for face in result[:1]:
                    flag = 1
                    gender = face['faceAttributes']['gender']
                    age = face['faceAttributes']['age']
                    print(gender, age)
                    rect = face['faceRectangle']
                    width = rect['width']
                    top = rect['top']
                    height = rect['height']
                    left = rect['left']

class Player(threading.Thread):
    def __init__(self, flag_mutex, vid_name):
        self.mutex = flag_mutex
        self.vid = vid_name
        self.running = False
        threading.Thread.__init__(self)

    def run(self):
        self.running = True
        global ad_playing
        with (self.mutex):
            ad_playing = True
        img = imread(self.vid)
        for i in range(100):
            cv2.imshow('ad', img)
            cv2.waitKey(1)
            sleep(0.03)

        # capvid = cv2.VideoCapture('vids/' + self.vid)
        # print("playing video " + self.vid)
        # while capvid.isOpened() and self.running:
        #     vret, vframe = capvid.read()
        #     if not vret:
        #         break
        #     cv2.imshow('ad', vframe)
        #     sleep(0.04)
        #     if (cv2.waitKey(1) & 0xFF == ord('d')):
        #         break
        self.running = False
        #capvid.release()
        cv2.destroyWindow('ad')
        with self.mutex:
            ad_playing = False

def categorize(age, gender):
    res = ""
    if (gender == "male"):
        res = "m"
    else:
        res = "f"
    if (age <= 18):
        res += "0"
    elif (age <= 30):
        res += "1"
    else:
        res += "2"
    return res


def recognize():
    cap = cv2.VideoCapture(0)
    time_reset = 0
    last_time = 0
    cur_time = 0
    mutex = threading.RLock()
    ad_mutex = threading.RLock()
    c = Cam(mutex)
    global width, top, height, left, gender, age, rgbf, flag

    while True:
        ret, frame = cap.read()
        with mutex:
            rgbf = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if (not c.running):
            c.start()

        with mutex:
            cv2.rectangle(frame, (left, top), (left + width, top + height),
                        (0, 255, 0), 2)
            cv2.putText(frame, '{},{}'.format(gender, int(age)), (left, top),
                      cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

        cv2.imshow('Demo', frame)
        cur_time = time.process_time()
        if (flag):
            if (not ad_playing):
                with mutex:
                    vid_link = categorize(age, gender)
                p = Player(ad_mutex, vid_link + ".gif")
                p.start()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    c.running = False
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0/'
    KEY = "c57f590000e541b8a1f124d6eaef6d8f"
    CF.Key.set(KEY)
    CF.BaseUrl.set(BASE_URL)
    recognize()
