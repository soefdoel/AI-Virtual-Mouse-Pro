# hand_tracker.py

import cv2
import mediapipe as mp
import config

class HandTracker:
    """
    Kelas untuk membungkus semua fungsionalitas deteksi tangan MediaPipe.
    """
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.drawing_utils = mp.solutions.drawing_utils
        self.results = None

    def process_frame(self, frame):
        """
        Memproses satu frame untuk mendeteksi tangan.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self

    def get_landmarks(self):
        """
        Mengembalikan landmark dari tangan yang terdeteksi.
        Saat ini hanya mendukung satu tangan.
        """
        if self.results and self.results.multi_hand_landmarks:
            return self.results.multi_hand_landmarks[0] # Ambil tangan pertama
        return None

    def draw_landmarks(self, frame):
        """
        Menggambar landmark pada frame jika tangan terdeteksi.
        """
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.drawing_utils.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        return frame