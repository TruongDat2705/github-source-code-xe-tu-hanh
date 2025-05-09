import socket
import cv2
import numpy as np
import time
import json
import base64
import os

global sendBack_angle, sendBack_Speed, current_speed, current_angle, radius
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0
count = 0 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
PORT = 54321
s.connect(('127.0.0.1', PORT))


def Control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed
    
error_arr = np.zeros(5)
pre_t = time.time()
MAX_SPEED = 60

def PID(error, p, i, d):
    global pre_t, error_arr
    error_arr[1:] = error_arr[0:-1]
    error_arr[0] = error
    P = error * p
    delta_t = time.time() - pre_t
    pre_t = time.time()
    if delta_t != 0:
        D = (error - error_arr[1]) / delta_t * d
    else:
        D = 0
    I = np.sum(error_arr) * delta_t * i
    angle = P + I + D
    if abs(angle) > 25:
        angle = np.sign(angle) * 25
    return int(angle)

if __name__ == "__main__":
    count = 0 #test
    os.makedirs('./Img', exist_ok=True) #test
    try:
        while True:
            """
            - Chương trình đưa cho bạn 1 giá trị đầu vào:
                * image: hình ảnh trả về từ xe
                * current_speed: vận tốc hiện tại của xe
                * current_angle: góc bẻ lái hiện tại của xe
            - Bạn phải dựa vào giá trị đầu vào này để tính toán và gán lại góc lái và tốc độ xe vào 2 biến:
                
                * Biến điều khiển: sendBack_angle, sendBack_Speed
                Trong đó:
                    + sendBack_angle (góc điều khiển): [-25, 25]
                        NOTE: ( âm là góc trái, dương là góc phải)
                    + sendBack_Speed (tốc độ điều khiển): [-150, 150]
                        NOTE: (âm là lùi, dương là tiến)
            """
            message = bytes(f"{sendBack_angle} {sendBack_Speed}", "utf-8")
            s.sendall(message)
            data = s.recv(100000)
            data_recv = json.loads(data)
            
            current_angle = data_recv["Angle"]
            current_speed = data_recv["Speed"]
            
            jpg_original = base64.b64decode(data_recv["Img"])
            jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            image = cv2.imdecode(jpg_as_np, flags=1)


            #test
            count += 1
            img_name = "./Img/Img_{}.jpg".format(count)
            cv2.imwrite(img_name, image)
            key = cv2.waitKey(10)

            # your process here
            # -------------------------------------------Workspace---------------------------------- #
        
            angle_setpoint = PID(error=1, p=1, i=1, d=1)
            print(current_speed, current_angle)
            
        
            cv2.imshow('Image Original', image)
            angle = 10 
            speed = 20
            Control(angle, speed)
                
                
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print('closing socket')
        s.close()