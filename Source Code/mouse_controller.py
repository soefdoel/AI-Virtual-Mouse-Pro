# mouse_controller.py

import pyautogui
import time
import config

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.is_locked = False
        self.is_mouse_active = False
        self.is_dragging = False
        self.is_scrolling = False
        self.is_swiping = False
        self.is_4_finger_swiping = False # <<< VARIABEL STATUS BARU
        self.is_media_mode = False
        self.swipe_mode = None

        # Variabel untuk konfirmasi gestur LOCK/UNLOCK
        self.potential_lock_gesture = None
        self.gesture_lock_timer = 0

        self.prev_hand_x, self.prev_hand_y = 0, 0
        self.prev_cursor_x, self.prev_cursor_y = 0, 0
        self.prev_scroll_y = 0
        self.swipe_start_x, self.swipe_start_y = 0, 0
        self.prev_swipe_x = 0
        self.last_action_time = 0
        self.media_control_start_x, self.media_control_start_y = 0, 0 # <<< VARIABEL BARU
    
    # >>> LOGIKA LOCK/UNLOCK KEMBALI KE METODE INI DENGAN GESTUR BARU <<<
    def handle_lock_mode(self, gesture):
        """Mengelola status lock/unlock dengan gestur L dan Call Me."""
        lock_gestures = ["L_SHAPE", "CALL_ME_SHAPE"]

        if gesture not in lock_gestures:
            self.potential_lock_gesture = None; self.gesture_lock_timer = 0
            return
        
        if gesture != self.potential_lock_gesture:
            self.potential_lock_gesture = gesture; self.gesture_lock_timer = time.time()
            return
        
        if time.time() - self.gesture_lock_timer > config.GESTURE_CONFIRM_DURATION:
            if self.potential_lock_gesture == "L_SHAPE" and not self.is_locked:
                self.is_locked = True
                print("PROGRAM LOCKED")
            elif self.potential_lock_gesture == "CALL_ME_SHAPE" and self.is_locked:
                self.is_locked = False
                print("PROGRAM UNLOCKED")
            
            self.potential_lock_gesture = None; self.gesture_lock_timer = 0

    # >>> LOGIKA HANDLE_ACTIONS DISEDERHANAKAN KEMBALI <<<
    def handle_actions(self, gesture):
        if not self.is_mouse_active: return
        current_time = time.time()
        if current_time - self.last_action_time < config.CLICK_COOLDOWN: return
        
        if gesture == "PINCH_MIDDLE_THUMB" and not self.is_dragging:
            pyautogui.mouseDown(button='left'); self.is_dragging = True; self.last_action_time = current_time; print("Drag Started")
            return
        if gesture != "PINCH_MIDDLE_THUMB" and self.is_dragging:
            pyautogui.mouseUp(button='left'); self.is_dragging = False; self.last_action_time = current_time; print("Drag Ended (Drop)")
            return

        if not self.is_dragging:
            if gesture == "PINCH_INDEX_THUMB":
                pyautogui.hotkey('win', 'a'); self.last_action_time = current_time; print("4-Finger Tap: Opened Action Center")
            elif gesture == "PINCH_RING_THUMB":
                pyautogui.click(button='right'); self.last_action_time = current_time; print("Right Click!")
            elif gesture == "PINCH_PINKY_THUMB":
                pyautogui.hotkey('win', 's'); self.last_action_time = current_time; print("3-Finger Tap: Opened Search")

    def update_state(self, gesture):
        """Mengubah status mouse (aktif/nonaktif) secara instan."""
        if self.is_scrolling or self.is_swiping or self.is_4_finger_swiping:
            return

        if gesture == "FIVE_FINGER_SPREAD" and not self.is_mouse_active:
            print("Mode Mouse: AKTIF"); self.is_mouse_active = True
            self.prev_cursor_x, self.prev_cursor_y = pyautogui.position()
        
        elif gesture == "FIST" and self.is_mouse_active:
            print("Mode Mouse: NONAKTIF"); self.is_mouse_active = False
            self.prev_hand_x, self.prev_hand_y = 0, 0
    
    # ... (Metode move dan handle_scrolling tetap sama) ...
    def move(self, hand_landmarks, frame_shape):
        if not self.is_mouse_active: return None, None
        frame_h, frame_w = frame_shape; index_tip = hand_landmarks.landmark[8]
        ix = int(index_tip.x * frame_w); iy = int(index_tip.y * frame_h)
        if self.prev_hand_x != 0:
            dx = (ix - self.prev_hand_x) * config.SENSITIVITY; dy = (iy - self.prev_hand_y) * config.SENSITIVITY
            target_x = self.prev_cursor_x + dx; target_y = self.prev_cursor_y + dy
            current_x = self.prev_cursor_x + (target_x - self.prev_cursor_x) / config.SMOOTHING_FACTOR
            current_y = self.prev_cursor_y + (target_y - self.prev_cursor_y) / config.SMOOTHING_FACTOR
            pyautogui.moveTo(current_x, current_y)
            self.prev_cursor_x, self.prev_cursor_y = current_x, current_y
        self.prev_hand_x, self.prev_hand_y = ix, iy
        return ix, iy

    def handle_scrolling(self, gesture, hand_landmarks, frame_shape):
        if self.is_mouse_active: self.is_scrolling = False; return
        frame_h, frame_w = frame_shape; index_y = int(hand_landmarks.landmark[8].y * frame_h)
        middle_y = int(hand_landmarks.landmark[12].y * frame_h); current_scroll_y = (index_y + middle_y) // 2
        if gesture == "TWO_FINGER_SCROLL" and not self.is_scrolling:
            self.is_scrolling = True; self.prev_scroll_y = current_scroll_y; print("Mode Scroll: ON")
        elif gesture == "TWO_FINGER_SCROLL" and self.is_scrolling:
            dy = current_scroll_y - self.prev_scroll_y
            if abs(dy) > 2:
                scroll_amount = -int(dy / config.SCROLL_SENSITIVITY)
                if scroll_amount != 0: pyautogui.scroll(scroll_amount)
            self.prev_scroll_y = current_scroll_y
        elif gesture != "TWO_FINGER_SCROLL" and self.is_scrolling:
            self.is_scrolling = False; self.prev_scroll_y = 0; print("Mode Scroll: OFF")

    # ... (Metode handle_swiping tetap sama) ...
    def handle_swiping(self, gesture, hand_landmarks, frame_shape):
        if self.is_mouse_active:
            if self.is_swiping: pyautogui.keyUp('alt'); self.is_swiping = False; self.swipe_mode = None
            return
        frame_h, frame_w = frame_shape; center_x = int(hand_landmarks.landmark[9].x * frame_w); center_y = int(hand_landmarks.landmark[9].y * frame_h)
        if gesture == "THREE_FINGER_SWIPE" and not self.is_swiping:
            self.is_swiping = True; self.swipe_start_x, self.swipe_start_y = center_x, center_y; print("Swipe Ready...")
        elif self.is_swiping:
            dx = center_x - self.swipe_start_x; dy = center_y - self.swipe_start_y
            if self.swipe_mode is None:
                if abs(dx) > config.SWIPE_ACTIVATION_DISTANCE or abs(dy) > config.SWIPE_ACTIVATION_DISTANCE:
                    if abs(dx) > abs(dy):
                        self.swipe_mode = 'HORIZONTAL'; pyautogui.keyDown('alt'); pyautogui.press('tab')
                        self.prev_swipe_x = center_x; print("App Switcher: ACTIVATED")
                    else:
                        self.swipe_mode = 'VERTICAL'; print("Vertical Swipe Activated")
            if self.swipe_mode == 'VERTICAL':
                if dy < -config.SWIPE_TRIGGER_DISTANCE:
                    print("Swipe Up: Task View"); pyautogui.hotkey('win', 'tab'); self.is_swiping = False
                elif dy > config.SWIPE_TRIGGER_DISTANCE:
                    print("Swipe Down: Show Desktop"); pyautogui.hotkey('win', 'd'); self.is_swiping = False
            elif self.swipe_mode == 'HORIZONTAL':
                nav_dx = center_x - self.prev_swipe_x
                if nav_dx > config.SWIPE_TRIGGER_DISTANCE:
                    pyautogui.press('tab'); self.prev_swipe_x = center_x; print("App Switcher: Navigate Right")
                elif nav_dx < -config.SWIPE_TRIGGER_DISTANCE:
                    pyautogui.keyDown('shift'); pyautogui.press('tab'); pyautogui.keyUp('shift')
                    self.prev_swipe_x = center_x; print("App Switcher: Navigate Left")
        if gesture != "THREE_FINGER_SWIPE" and self.is_swiping:
            if self.swipe_mode == 'HORIZONTAL': pyautogui.keyUp('alt'); print("App Switcher: SELECTION CONFIRMED")
            self.is_swiping = False; self.swipe_mode = None; print("Swipe Mode: OFF")

    # >>> METODE BARU UNTUK SWIPE 4 JARI <<<
    def handle_4_finger_swipe(self, gesture, hand_landmarks, frame_shape):
        if self.is_mouse_active: self.is_4_finger_swiping = False; return
        
        frame_h, frame_w = frame_shape
        center_x = int(hand_landmarks.landmark[9].x * frame_w)

        # Memulai mode swipe
        if gesture == "FOUR_FINGER_SWIPE" and not self.is_4_finger_swiping:
            self.is_4_finger_swiping = True
            self.swipe_start_x = center_x
            print("4-Finger Swipe Mode: ON")
        
        # Saat sedang dalam mode swipe
        elif gesture == "FOUR_FINGER_SWIPE" and self.is_4_finger_swiping:
            dx = center_x - self.swipe_start_x
            
            # Swipe ke kanan -> Pindah Virtual Desktop Kanan
            if dx > config.SWIPE_TRIGGER_DISTANCE:
                pyautogui.hotkey('ctrl', 'win', 'right')
                print("Switched to Next Virtual Desktop")
                self.is_4_finger_swiping = False # Aksi sekali tembak, langsung reset
            
            # Swipe ke kiri -> Pindah Virtual Desktop Kiri
            elif dx < -config.SWIPE_TRIGGER_DISTANCE:
                pyautogui.hotkey('ctrl', 'win', 'left')
                print("Switched to Previous Virtual Desktop")
                self.is_4_finger_swiping = False # Aksi sekali tembak, langsung reset

        # Menghentikan mode jika gestur berubah
        elif gesture != "FOUR_FINGER_SWIPE" and self.is_4_finger_swiping:
            self.is_4_finger_swiping = False
            print("4-Finger Swipe Mode: OFF")
    
    # >>> METODE BARU UNTUK KONTROL MEDIA <<<
    def handle_media_control(self, gesture, hand_landmarks, frame_shape):
        if self.is_mouse_active: self.is_media_mode = False; return

        frame_h, frame_w = frame_shape
        center_x = int(hand_landmarks.landmark[9].x * frame_w)
        center_y = int(hand_landmarks.landmark[9].y * frame_h)

        # Masuk ke Mode Media
        if gesture == "ROCK_ON" and not self.is_media_mode:
            self.is_media_mode = True
            self.media_control_start_x, self.media_control_start_y = center_x, center_y
            print("Media Mode: ON")

        # Saat sedang dalam Mode Media
        elif self.is_media_mode:
            # Aksi Tap (sekali tekan)
            if time.time() - self.last_action_time > config.CLICK_COOLDOWN:
                if gesture == "POINTING": # Menggunakan gestur telunjuk yang sudah ada
                    pyautogui.press('space'); self.last_action_time = time.time(); print("Media: Play/Pause")
                elif gesture == "PINKY_UP":
                    pyautogui.press('f'); self.last_action_time = time.time(); print("Media: Fullscreen")

            # Aksi Gerakan (Volume & Seek)
            dx = center_x - self.media_control_start_x
            dy = center_y - self.media_control_start_y

            if abs(dx) > config.MEDIA_CONTROL_THRESHOLD:
                if dx > 0: pyautogui.press('right'); print("Media: Seek Forward")
                else: pyautogui.press('left'); print("Media: Seek Backward")
                self.media_control_start_x = center_x # Reset posisi
            
            if abs(dy) > config.MEDIA_CONTROL_THRESHOLD:
                if dy > 0: pyautogui.press('down'); print("Media: Volume Down")
                else: pyautogui.press('up'); print("Media: Volume Up")
                self.media_control_start_y = center_y # Reset posisi

        # >>> PERUBAHAN DI SINI: Keluar dari Mode Media dengan FIST <<<
        if gesture == "FIST" and self.is_media_mode:
            self.is_media_mode = False
            print("Media Mode: OFF")