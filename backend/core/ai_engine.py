"""
Backend AI Face Recognition Engine for Smart Attendance System
Uses dlib-based face_recognition library (128-D ResNet Vector) for Face Identification.
Reference project: C:/Users/shinj/face_recognition
"""

import os
import cv2
import numpy as np
import face_recognition

# Configurable matching threshold (dlib face_recognition distance threshold)
# 0.65 is optimal for mobile cameras and multi-angle classroom recognition
MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.65"))


import io
from PIL import Image, ImageOps

def ensure_8bit_rgb(img):
    """
    Guarantees that the input is a C-contiguous 8-bit unsigned integer RGB image
    with exactly 3 channels (H, W, 3), strictly satisfying dlib's is_image_type() check.
    Prevents dlib 'Unsupported image type, must be 8bit gray or RGB image.' errors.
    """
    if img is None:
        return None

    if not isinstance(img, np.ndarray):
        img = np.array(img)

    # If 4 channels (RGBA / BGRA), convert to 3 channels RGB
    if img.ndim == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    elif img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.ndim == 3 and img.shape[2] == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif img.ndim == 3 and img.shape[2] > 3:
        img = img[:, :, :3]

    # Ensure dtype is uint8 (8-bit unsigned integer)
    if img.dtype != np.uint8:
        if img.dtype in (np.float32, np.float64):
            if img.max() <= 1.0:
                img = (img * 255.0).clip(0, 255).astype(np.uint8)
            else:
                img = img.clip(0, 255).astype(np.uint8)
        else:
            img = img.astype(np.uint8)

    # Strictly ensure C-contiguous memory layout
    if not img.flags['C_CONTIGUOUS']:
        img = np.ascontiguousarray(img, dtype=np.uint8)

    return img


def decode_image_with_exif(photo_bytes, max_dim=1200):
    """
    Decodes image bytes, auto-corrects mobile phone EXIF camera orientation,
    and downscales if greater than max_dim for fast, low-memory dlib inference.
    Returns guaranteed 8-bit RGB C-contiguous numpy array with shape (H, W, 3).
    """
    if not photo_bytes:
        return None

    try:
        pil_img = Image.open(io.BytesIO(photo_bytes))
        try:
            pil_img = ImageOps.exif_transpose(pil_img)
        except Exception:
            pass

        if pil_img.mode != 'RGB':
            pil_img = pil_img.convert('RGB')

        w, h = pil_img.size
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        arr = np.array(pil_img, dtype=np.uint8)
        return ensure_8bit_rgb(arr)

    except Exception as e:
        print(f"[AI] PIL decode fallback: {e}")
        try:
            nparr = np.frombuffer(photo_bytes, np.uint8)
            bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if bgr is not None:
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                return ensure_8bit_rgb(rgb)
        except Exception as e2:
            print(f"[AI] OpenCV fallback error: {e2}")

    return None


def detect_all_faces(img_rgb):
    """
    Detects ALL face bounding boxes in an image using face_recognition (HOG model)
    with safe single-scale upsampling and OpenCV Haar Cascade fallback.
    Returns list of (x, y, w, h) tuples.
    """
    img_rgb = ensure_8bit_rgb(img_rgb)
    if img_rgb is None or img_rgb.size == 0 or img_rgb.shape[0] < 20 or img_rgb.shape[1] < 20:
        return []

    locations = []
    try:
        locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=1)
        if len(locations) == 0:
            locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=0)
    except Exception as e:
        print(f"[AI] face_locations error: {e}")

    bboxes = []
    for (top, right, bottom, left) in locations:
        x = left
        y = top
        w = right - left
        h = bottom - top
        bboxes.append((int(x), int(y), int(w), int(h)))

    if len(bboxes) == 0:
        try:
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            for (x, y, w, h) in faces:
                bboxes.append((int(x), int(y), int(w), int(h)))
        except Exception:
            pass

    return bboxes


def generate_image_encodings(img_rgb):
    """
    Detects faces and extracts 128-D dlib ResNet face encodings directly from full image.
    Returns list of (bbox_tuple, 128D_list) tuples.
    """
    img_rgb = ensure_8bit_rgb(img_rgb)
    if img_rgb is None or img_rgb.size == 0 or img_rgb.shape[0] < 20 or img_rgb.shape[1] < 20:
        return []

    try:
        locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=1)
        if len(locations) == 0:
            locations = face_recognition.face_locations(img_rgb, number_of_times_to_upsample=0)

        if len(locations) == 0:
            return []

        encodings = face_recognition.face_encodings(img_rgb, known_face_locations=locations)
        results = []
        for loc, enc in zip(locations, encodings):
            top, right, bottom, left = loc
            bbox = (int(left), int(top), int(right - left), int(bottom - top))
            results.append((bbox, enc.astype(np.float32).tolist()))

        return results
    except Exception as e:
        print(f"[AI] generate_image_encodings error: {e}")
        return []


def crop_and_preprocess_face(img_rgb, bbox):
    """
    Crops face region with 15% outer padding expansion, ensuring bounds and C-contiguous layout.
    """
    img_rgb = ensure_8bit_rgb(img_rgb)
    if img_rgb is None or img_rgb.size == 0:
        return None

    img_h, img_w = img_rgb.shape[:2]
    x, y, w, h = bbox

    pad_w = int(w * 0.15)
    pad_h = int(h * 0.15)

    left = max(0, min(img_w - 1, x - pad_w))
    top = max(0, min(img_h - 1, y - pad_h))
    right = max(left + 10, min(img_w, x + w + pad_w))
    bottom = max(top + 10, min(img_h, y + h + pad_h))

    crop = img_rgb[top:bottom, left:right]
    if crop.size == 0 or crop.shape[0] < 10 or crop.shape[1] < 10:
        return None

    return ensure_8bit_rgb(crop)


def generate_embedding(face_rgb):
    """
    Runs dlib face_recognition 128-D model inference on face image.
    Returns 128-D numpy float array as python list.
    """
    if face_rgb is None:
        return []
    face_rgb = ensure_8bit_rgb(face_rgb)
    if face_rgb is None or face_rgb.shape[0] < 20 or face_rgb.shape[1] < 20:
        return []

    try:
        encodings = face_recognition.face_encodings(face_rgb)
        if len(encodings) > 0:
            return encodings[0].astype(np.float32).tolist()

        h, w = face_rgb.shape[:2]
        if h >= 20 and w >= 20:
            loc = [(0, w, h, 0)]
            encodings = face_recognition.face_encodings(face_rgb, known_face_locations=loc)
            if len(encodings) > 0:
                return encodings[0].astype(np.float32).tolist()
    except Exception as e:
        print(f"[AI] generate_embedding error: {e}")

    return []


def euclidean_distance(emb1, emb2):
    """
    Calculates L2 Euclidean distance between two 128-D face_recognition encodings.
    Handles JSON string or float array safely.
    """
    import json
    if isinstance(emb1, str):
        try:
            emb1 = json.loads(emb1)
        except Exception:
            pass
    if isinstance(emb2, str):
        try:
            emb2 = json.loads(emb2)
        except Exception:
            pass
    a = np.array(emb1, dtype=np.float32)
    b = np.array(emb2, dtype=np.float32)
    return float(np.linalg.norm(a - b))


def match_face_to_students(query_embedding, class_students, threshold=MATCH_THRESHOLD):
    """
    Compares query_embedding against enrolled class students using face_recognition distance.
    Returns (best_student_user, best_distance, confidence_score) or (None, actual_closest_distance, 0.0)
    """
    if not query_embedding:
        return None, 999.0, 0.0

    best_student = None
    best_distance = float('inf')

    for student in class_students:
        emb = student.face_embedding
        if not emb:
            continue

        try:
            dist = euclidean_distance(query_embedding, emb)
            if dist < best_distance:
                best_distance = dist
                best_student = student
        except Exception as e:
            print(f"[AI] Distance error for {student.username}: {e}")

    if best_student and best_distance < threshold:
        confidence = round(float(1.0 - (best_distance / threshold)), 4)
        print(f"[AI MATCH] Recognized: {best_student.username} (dist: {best_distance:.4f}, conf: {confidence:.2f})")
        return best_student, round(best_distance, 4), max(0.0, confidence)

    closest_dist = round(best_distance, 4) if best_distance != float('inf') else 999.0
    print(f"[AI UNMATCHED] Closest face was {best_student.username if best_student else 'None'} at dist {closest_dist:.4f} (threshold: {threshold})")
    return None, closest_dist, 0.0


def process_classroom_photos(photo_bytes_list, class_students, threshold=MATCH_THRESHOLD, progress_callback=None):
    """
    Processes multiple classroom photos using face_recognition library:
    1. Detects faces in every photo.
    2. Generates 128-D dlib vector embedding per face.
    3. Matches against class students.
    4. Deduplicates present students.
    5. Returns draft attendance results.
    """
    present_student_ids = set()
    match_details = []
    total_faces_detected = 0
    unmatched_faces_count = 0

    for idx, photo_bytes in enumerate(photo_bytes_list):
        img = decode_image_with_exif(photo_bytes)

        if img is None:
            if progress_callback:
                try:
                    progress_callback(idx + 1, len(photo_bytes_list), 0)
                except Exception:
                    pass
            continue

        face_data = generate_image_encodings(img)
        total_faces_detected += len(face_data)

        if len(face_data) == 0:
            bboxes = detect_all_faces(img)
            for bbox in bboxes:
                crop = crop_and_preprocess_face(img, bbox)
                if crop is not None:
                    emb = generate_embedding(crop)
                    if emb:
                        face_data.append((bbox, emb))

        if progress_callback:
            try:
                progress_callback(idx + 1, len(photo_bytes_list), len(face_data))
            except Exception:
                pass

        for bbox, embedding in face_data:
            matched_student, dist, conf = match_face_to_students(embedding, class_students, threshold=threshold)

            if matched_student:
                present_student_ids.add(matched_student.id)
                match_details.append({
                    'photo_index': idx + 1,
                    'student_id': matched_student.id,
                    'student_name': f"{matched_student.first_name} {matched_student.last_name}".strip() or matched_student.username,
                    'roll_number': matched_student.roll_number,
                    'distance': dist,
                    'confidence': conf
                })
            else:
                unmatched_faces_count += 1
                match_details.append({
                    'photo_index': idx + 1,
                    'student_id': None,
                    'student_name': "Unmatched Face",
                    'roll_number': None,
                    'distance': dist,
                    'confidence': 0.0
                })

    # Class-scoped student breakdown
    present_students = []
    absent_students = []

    for st in class_students:
        name = f"{st.first_name} {st.last_name}".strip() or st.username
        pic_url = None
        try:
            if st.profile_picture and hasattr(st.profile_picture, 'url'):
                pic_url = st.profile_picture.url
                if not pic_url.startswith('/') and not pic_url.startswith('http'):
                    pic_url = '/' + pic_url
        except Exception:
            pic_url = None

        st_info = {
            'id': st.id,
            'username': st.username,
            'name': name,
            'roll_number': st.roll_number,
            'has_registered_face': bool(st.face_embedding),
            'profile_picture': pic_url
        }
        if st.id in present_student_ids:
            present_students.append(st_info)
        else:
            absent_students.append(st_info)

    return {
        'total_photos_processed': len(photo_bytes_list),
        'total_faces_detected': total_faces_detected,
        'unmatched_faces_count': unmatched_faces_count,
        'present_count': len(present_students),
        'absent_count': len(absent_students),
        'present_students': present_students,
        'absent_students': absent_students,
        'match_details': match_details
    }
