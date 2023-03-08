import threading

import cv2
import keyboard
import mediapipe as mp
import numpy as np
import pyautogui
import win32api
import win32con

pyautogui.FAILSAFE = True

# 定义全局变量img_cv2
img_cv2 = None

def get_head_position(image):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # 将图片转换为RGB格式，并执行pose estimation
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        
        # 繪製骨架
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 检查是否检测到了pose
        if results.pose_landmarks is None:
            return None

        # 获取头部位置
        head_landmark = results.pose_landmarks.landmark[0]
        return (int(head_landmark.x * image.shape[1]), int(head_landmark.y * image.shape[0]))



def get_chest_landmark(image):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # 定義 mediapipe pose detector
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # 將影像轉換為灰階
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 偵測人體姿勢
        results = pose.process(image_gray)

        # 如果偵測到人體姿勢
        if results.pose_landmarks is not None:
            # 取得胸口的 landmark
            chest_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

            # 取得胸口在圖像中的座標
            image_height, image_width, _ = image.shape
            cx, cy = int(chest_landmark.x * image_width), int(chest_landmark.y * image_height)

            return cx, cy
        else:
            return None


def mouse_callback(event, x, y, flags, params):
    global img_cv2
    if event == cv2.EVENT_MOUSEMOVE:
        # 在畫面上標示出滑鼠位置
        
        # create a copy of the original image
        img_copy = img_cv2.copy()
        # draw a circle on the copy
        cv2.circle(img_copy, (x, y), 5, (0, 255, 0), 2)
        # show the updated image
        cv2.imshow("Screen", img_copy)


def capture_screen():
    global img_cv2  # 声明使用全局变量
    
    # 设置窗口名
    cv2.namedWindow("Screen", cv2.WINDOW_NORMAL)

    # 设置窗口位置
    cv2.moveWindow("Screen", 1920, 1)

    cv2.setMouseCallback('Screen', mouse_callback)
    
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    # 定義MediaPipe姿勢估計模型
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    while True:
        # 獲取螢幕畫面
        img = pyautogui.screenshot()

        # 轉換為 OpenCV 格式
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # 從RGB影像中偵測人體姿勢
        results = pose.process(img_cv2)
    
        # 繪製骨架
        mp_drawing.draw_landmarks(img_cv2, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 顯示螢幕畫面
        cv2.imshow("Screen", img_cv2)

        # 按下 Q 鍵退出循環
        if cv2.waitKey(1) == ord("q"):
            break

    # 關閉視窗
    cv2.destroyAllWindows()

    
def on_press(event):
    global img_cv2  # 声明使用全局变量
    
    if keyboard.is_pressed('caps lock'):
    
        # chest_position = get_chest_landmark(img_cv2)
        
        # if chest_position is not None:
        #     # 目前滑鼠的位置
        #     x0, y0 = win32api.GetCursorPos()

        #     # 目標位置的相對座標
        #     dx, dy = chest_position[0], chest_position[1]

        #     # 將相對座標轉換為 absolute coordinate 絕對座標系統
        #     x, y = dx - x0, dy - y0
            
        #     win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)
        # else:
        #     print("Unable to get head position.")
        
        
        head_position = get_head_position(img_cv2)
        
        if head_position is not None:
            
            # 目前滑鼠的位置
            x0, y0 = win32api.GetCursorPos()

            # 目標位置的相對座標
            dx, dy = head_position[0], head_position[1]

            # 將相對座標轉換為 absolute coordinate 絕對座標系統
            x, y = dx - x0, dy - y0
            
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)
        else:
            print("Unable to get head position.")


if __name__ == "__main__":
    # 启动截图线程
    capture_screen_thread = threading.Thread(target=capture_screen)
    capture_screen_thread.start()

    keyboard.on_press(on_press)
    




    # # 监听鼠标点击事件
    
    # from pynput import mouse

        
    # def on_move(x, y):
    #     print('Mouse moved to ({0}, {1})'.format(x, y))
    

    # with mouse.Listener(on_move=on_move,) as listener:
        # listener.join()

    
    #def on_click(x, y, button, pressed):
    #     global img_cv2  # 声明使用全局变量
    
    # if button == mouse.Button.middle and pressed:
        # pyautogui.moveTo(get_head_position(img_cv2)[0], get_head_position(img_cv2)[1], duration=0.1, tween=pyautogui.easeInOutQuad)

    
    # with mouse.Listener(on_click=on_click) as listener:
    #     listener.join()