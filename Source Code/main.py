# main.py

import cv2
from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from mouse_controller import MouseController
import config

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    detector = GestureDetector()
    controller = MouseController()

    while True:
        success, frame = cap.read()
        if not success: break
        frame = cv2.flip(frame, 1)
        frame_height, frame_width, _ = frame.shape

        landmarks = tracker.process_frame(frame).get_landmarks()
        
        if landmarks:
            gesture = detector.detect(landmarks, (frame_height, frame_width))
            
            controller.handle_lock_mode(gesture)
            
            if not controller.is_locked:
                controller.update_state(gesture)

                if controller.is_mouse_active:
                    ix, iy = controller.move(landmarks, (frame_height, frame_width))
                    controller.handle_actions(gesture)
                    if ix is not None: cv2.circle(frame, (ix, iy), 15, (0, 255, 0), cv2.FILLED)
                else: # Mode NONAKTIF
                    controller.handle_scrolling(gesture, landmarks, (frame_height, frame_width))
                    controller.handle_swiping(gesture, landmarks, (frame_height, frame_width))
                    controller.handle_4_finger_swipe(gesture, landmarks, (frame_height, frame_width))
                    # >>> PANGGIL FUNGSI KONTROL MEDIA <<<
                    controller.handle_media_control(gesture, landmarks, (frame_height, frame_width))
                    
                    # Visual feedback
                    if controller.is_scrolling:
                        for i in [8, 12]:
                            px = int(landmarks.landmark[i].x * frame_width); py = int(landmarks.landmark[i].y * frame_height)
                            cv2.circle(frame, (px, py), 15, (255, 0, 255), cv2.FILLED)
                    elif controller.is_swiping:
                        for i in [8, 12, 16]:
                            px = int(landmarks.landmark[i].x * frame_width); py = int(landmarks.landmark[i].y * frame_height)
                            cv2.circle(frame, (px, py), 15, (255, 255, 0), cv2.FILLED)
                    elif controller.is_4_finger_swiping:
                        for i in [8, 12, 16, 20]:
                            px = int(landmarks.landmark[i].x * frame_width); py = int(landmarks.landmark[i].y * frame_height)
                            cv2.circle(frame, (px, py), 15, (0, 165, 255), cv2.FILLED)
                    # >>> VISUAL FEEDBACK BARU UNTUK MODE MEDIA <<<
                    elif controller.is_media_mode:
                        for i in [8, 20]: # Jari telunjuk dan kelingking
                            px = int(landmarks.landmark[i].x * frame_width); py = int(landmarks.landmark[i].y * frame_height)
                            cv2.circle(frame, (px, py), 15, (203, 192, 255), cv2.FILLED) # Warna Lavender

            frame = tracker.draw_landmarks(frame)

        # Tampilkan status di layar
        if controller.is_locked:
            status_text = "LOCKED"; text_color = (128, 128, 128)
        elif controller.is_mouse_active:
            status_text = "Mode: AKTIF"; text_color = (0, 255, 0)
        else: # Mode NONAKTIF
            status_text = "Mode: NONAKTIF"; text_color = (0, 0, 255)
            if controller.is_scrolling: status_text = "Mode: SCROLLING"; text_color = (255, 0, 255)
            elif controller.is_swiping: status_text = "Mode: 3-FINGER SWIPE"; text_color = (255, 255, 0)
            elif controller.is_4_finger_swiping: status_text = "Mode: 4-FINGER SWIPE"; text_color = (0, 165, 255)
            # >>> STATUS BARU <<<
            elif controller.is_media_mode: status_text = "Mode: MEDIA CONTROL"; text_color = (203, 192, 255)
            
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2, cv2.LINE_AA)
        cv2.imshow('AI Virtual Mouse Pro', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()