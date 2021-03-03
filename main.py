import time
from datetime import datetime, timedelta

import win32con
import win32gui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import win32api
import sys
import cv2
import sys

simulator_hwnd = win32gui.FindWindow(None, '逍遥模拟器')
recorder_hwnd = win32gui.FindWindow(None, 'MEmu')
print(simulator_hwnd, recorder_hwnd)


def start_record():
    win32gui.SetForegroundWindow(recorder_hwnd)
    # 特殊处理：SendMessage实现不了，所以用keybd_event
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(win32con.VK_F5, 0, 0, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_F5, 0, win32con.KEYEVENTF_KEYUP, 0)


def stop_record():
    win32gui.SetForegroundWindow(recorder_hwnd)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(win32con.VK_F6, 0, 0, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_F6, 0, win32con.KEYEVENTF_KEYUP, 0)


if __name__ == "__main__":
    hwnd_title = dict()


    def get_all_hwnd(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(get_all_hwnd, 0)

    for h, t in hwnd_title.items():
        if t is not "":
            print(h, t)

    captured_screen_path = "D:/captured_screen.jpg"
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen()

    interval = 5                # interval: 每隔多少秒就检测
    detect_face_start_time = 0  # detect_face_start_time: 检测的开始时间
    detect_face_s = 10          # detect_face_s: 多少秒内检测结果没有变化就开始录像
    is_recording = False        # is_recording: 是否在录像
    monitor_s = 3600 * 2        # monitor_s: 程序运行时长
    end_time = datetime.now() + timedelta(seconds=monitor_s)
    while datetime.now() < end_time:
        img = screen.grabWindow(simulator_hwnd).toImage()
        img.save(captured_screen_path)

        # Create the haar cascade
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Read the image
        image = cv2.imread(captured_screen_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        # 无人脸
        if len(faces) == 0:
            # 未开始录像
            if not is_recording:
                # 未开始检测
                if detect_face_start_time == 0:
                    detect_face_start_time = datetime.now()
                else:
                    if detect_face_start_time + timedelta(seconds=detect_face_s) <= datetime.now():
                        # 意味着舞蹈开始，那么开始录像
                        is_recording = True
                        detect_face_start_time = 0
                        print("{}开始录像".format(datetime.now()))
                        start_record()

        # 有人脸
        else:
            # 已开始录像
            if is_recording:
                # 未开始检测
                if detect_face_start_time == 0:
                    detect_face_start_time = datetime.now()
                else:
                    if detect_face_start_time + timedelta(seconds=detect_face_s) <= datetime.now():
                        # 意味着舞蹈结束，那么结束录像
                        is_recording = False
                        detect_face_start_time = 0
                        print("{}结束录像".format(datetime.now()))
                        stop_record()

        time.sleep(interval)

    print("{}结束录像".format(datetime.now()))
    stop_record()
