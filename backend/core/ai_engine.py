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

def decode_image_with_exif(photo_bytes, max_dim=1200):
    """
    Decodes image bytes, auto-corrects mobile phone EXIF camera orientation,
    and downscales if greater than max_dim for fast, low-memory dlib HOG inference.
    Returns BGR numpy image array.
    """
    try:
        pil_img = Image.open(io.BytesIO(photo_bytes))
        pil_img = ImageOps.exif_transpose(pil_img)
        w, h = pil_img.size
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            new_w = int(w * scale)
            new_h = int(h * scale)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        rgb = np.array(pil_img.convert('RGB'))
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr
    except Exception:
        nparr = np.frombuffer(photo_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def detect_all_faces(img_array):
    """
    Detects ALL face bounding boxes in an image using face_recognition (HOG model)
    with safe single-scale upsampling and OpenCV Haar Cascade fallback.
    Prevents Render 512MB RAM OOM crashes by avoiding 2x upsampling.
    Returns list of (x, y, w, h) tuples.
    """
    rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    locations = face_recognition.face_locations(rgb, number_of_times_to_upsample=1)
    if len(locations) == 0:
        locations = face_recognition.face_locations(rgb, number_of_times_to_upsample=0)
    
    bboxes = []
    for (top, right, bottom, left) in locations:
        x = left
        y = top
        w = right - left
        h = bottom - top
        bboxes.append((int(x), int(y), int(w), int(h)))

    if len(bboxes) == 0:
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
            for (x, y, w, h) in faces:
                bboxes.append((int(x), int(y), int(w), int(h)))
        except Exception:
            pass

    return bboxes


def generate_image_encodings(img_array):
    """
    Detects faces and extracts 128-D dlib ResNet face encodings directly from full image.
    Uses upsampled HOG detection for live mobile and webcam streams.
    Returns list of (bbox_tuple, 128D_list) tuples.
    """
    rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    
    # Try upsampled dlib HOG detection (upsample=1 detects faces reliably)
    locations = face_recognition.face_locations(rgb, number_of_times_to_upsample=1)
    
    if len(locations) == 0:
        # Fallback to standard HOG
        locations = face_recognition.face_locations(rgb, number_of_times_to_upsample=0)

    if len(locations) == 0:
        return []

    encodings = face_recognition.face_encodings(rgb, known_face_locations=locations)
    
    results = []
    for loc, enc in zip(locations, encodings):
        top, right, bottom, left = loc
        bbox = (int(left), int(top), int(right - left), int(bottom - top))
        results.append((bbox, enc.astype(np.float32).tolist()))
        
    return results


def crop_and_preprocess_face(img_array, bbox):
    """
    Crops face region with 10% outer padding expansion.
    """
    x, y, w, h = bbox
    img_h, img_w = img_array.shape[:2]

    pad_w = int(w * 0.1)
    pad_h = int(h * 0.1)

    left = max(0, x - pad_w)
    top = max(0, y - pad_h)
    right = min(img_w, x + w + pad_w)
    bottom = min(img_h, y + h + pad_h)

    crop = img_array[top:bottom, left:right]
    if crop.size == 0:
        crop = img_array[y:y+h, x:x+w]

    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    return rgb


def generate_embedding(face_rgb):
    """
    Runs dlib face_recognition 128-D model inference on face image.
    Returns 128-D numpy float array as python list.
    """
    encodings = face_recognition.face_encodings(face_rgb)
    if len(encodings) > 0:
        return encodings[0].astype(np.float32).tolist()
    
    h, w = face_rgb.shape[:2]
    if h > 0 and w > 0:
        loc = [(0, w, h, 0)]
        encodings = face_recognition.face_encodings(face_rgb, known_face_locations=loc)
        if len(encodings) > 0:
            return encodings[0].astype(np.float32).tolist()

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
