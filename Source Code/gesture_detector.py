# gesture_detector.py

import math
import config

class GestureDetector:
    def __init__(self):
        # ... (init tetap sama) ...
        pass

    def detect(self, landmarks, frame_shape):
        # ... (kode untuk mendapatkan hand_scale tetap sama) ...
        try:
            wrist = landmarks.landmark[0]
            middle_mcp = landmarks.landmark[9]
            hand_scale = math.hypot((wrist.x - middle_mcp.x) * frame_shape[1], (wrist.y - middle_mcp.y) * frame_shape[0])
            if hand_scale == 0: hand_scale = 1
        except (IndexError, AttributeError):
            return None

        # --- Definisi Status Jari ---
        is_index_up = landmarks.landmark[8].y < landmarks.landmark[6].y
        is_middle_up = landmarks.landmark[12].y < landmarks.landmark[10].y
        is_ring_up = landmarks.landmark[16].y < landmarks.landmark[14].y
        is_pinky_up = landmarks.landmark[20].y < landmarks.landmark[18].y
        is_thumb_out = abs(landmarks.landmark[4].x - landmarks.landmark[17].x) > abs(landmarks.landmark[1].x - landmarks.landmark[17].x)
        
        is_index_curled = landmarks.landmark[8].y > landmarks.landmark[6].y
        is_middle_curled = landmarks.landmark[12].y > landmarks.landmark[10].y
        is_ring_curled = landmarks.landmark[16].y > landmarks.landmark[14].y
        is_pinky_curled = landmarks.landmark[20].y > landmarks.landmark[18].y
        
        # --- Logika Deteksi Gestur (dengan urutan prioritas) ---

        # >>> GESTUR BARU: Mode Media (Rock On) <<<
        if is_index_up and is_pinky_up and is_middle_curled and is_ring_curled:
            return "ROCK_ON"
        
        # Gestur "Call Me" untuk Unlock
        if is_pinky_up and is_thumb_out and is_index_curled and is_middle_curled and is_ring_curled:
            return "CALL_ME_SHAPE"

        # >>> GESTUR BARU: Fullscreen (Kelingking saja) <<<
        if is_pinky_up and is_index_curled and is_middle_curled and is_ring_curled:
            return "PINKY_UP"
        
        # >>> GESTUR BARU UNTUK LOCK & UNLOCK <<<
        # Gestur "L" untuk Lock
        if is_index_up and is_thumb_out and is_middle_curled and is_ring_curled and is_pinky_curled:
            return "L_SHAPE"

        # >>> LOGIKA KEPAL TANGAN DISEDERHANAKAN <<<
        # Sekarang hanya ada satu gestur kepal yang tidak peduli posisi jempol.
        if is_index_curled and is_middle_curled and is_ring_curled and is_pinky_curled:
            return "FIST"
        
        # >>> GESTUR BARU: Tambahkan deteksi Pointing untuk Play/Pause di Mode Media <<<
        if is_index_up and is_middle_curled and is_ring_curled and is_pinky_curled:
            return "POINTING"

        # ... (sisa kode deteksi gestur lain tetap sama) ...
        if is_index_up and is_middle_up and is_ring_up and is_pinky_up and is_thumb_out:
            return "FIVE_FINGER_SPREAD"
        if is_index_up and is_middle_up and is_ring_up and is_pinky_up:
            return "FOUR_FINGER_SWIPE"
        if is_index_up and is_middle_up and is_ring_up and is_pinky_curled:
            return "THREE_FINGER_SWIPE"
        if is_index_up and is_middle_up and not is_ring_up and not is_pinky_up:
            return "TWO_FINGER_SCROLL"

        # Logika Pinch
        thumb_tip = landmarks.landmark[4]; index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]; ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        frame_h, frame_w = frame_shape
        tx = int(thumb_tip.x * frame_w); ty = int(thumb_tip.y * frame_h)
        ix = int(index_tip.x * frame_w); iy = int(index_tip.y * frame_h)
        mx = int(middle_tip.x * frame_w); my = int(middle_tip.y * frame_h)
        rx = int(ring_tip.x * frame_w); ry = int(ring_tip.y * frame_h)
        px = int(pinky_tip.x * frame_w); py = int(pinky_tip.y * frame_h)

        dist_pinch_index_px = math.hypot(ix - tx, iy - ty)
        dist_pinch_middle_px = math.hypot(mx - tx, my - ty)
        dist_pinch_ring_px = math.hypot(rx - tx, ry - ty)
        dist_pinch_pinky_px = math.hypot(px - tx, py - ty)
        
        normalized_dist_index = dist_pinch_index_px / hand_scale
        normalized_dist_middle = dist_pinch_middle_px / hand_scale
        normalized_dist_ring = dist_pinch_ring_px / hand_scale
        normalized_dist_pinky = dist_pinch_pinky_px / hand_scale

        if normalized_dist_index < config.NORMALIZED_CLICK_THRESHOLD: return "PINCH_INDEX_THUMB"
        if normalized_dist_middle < config.NORMALIZED_CLICK_THRESHOLD: return "PINCH_MIDDLE_THUMB"
        if normalized_dist_ring < config.NORMALIZED_CLICK_THRESHOLD: return "PINCH_RING_THUMB"
        if normalized_dist_pinky < config.NORMALIZED_CLICK_THRESHOLD: return "PINCH_PINKY_THUMB"
            
        return None