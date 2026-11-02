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
# 0.75 is optimal for real-world mobile selfie cameras, room lighting, and multi-angle recognition
MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.75"))


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


def decode_image_with_exif(photo_bytes, max_dim=1600):
    """
    Decodes image bytes, auto-corrects mobile phone EXIF camera orientation,
    and downscales if greater than max_dim (1600px retains fine classroom face details).
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


def generate_image_encodings(img_rgb):
    """
    Robust Multi-Scale & Orientation-Tolerant Face Detection & 128-D ResNet Extraction:
    1. Ensures 8-bit C-contiguous RGB layout.
    2. Runs dlib HOG (upsample=1).
    3. If 0 faces found, runs dlib HOG (upsample=2) for smaller/farther classroom faces.
    4. If 0 faces found, runs OpenCV Haar Cascade (frontal default + frontal alt2) directly on full frame with 15% landmark context padding.
    5. If 0 faces found, tests 90-degree rotations (auto-correcting mobile photos with stripped EXIF orientation).
    Returns list of (bbox_tuple, 128D_list) tuples.
    """
    img_rgb = ensure_8bit_rgb(img_rgb)
    if img_rgb is None or img_rgb.size == 0 or img_rgb.shape[0] < 20 or img_rgb.shape[1] < 20:
        return []

    def _extract_from_frame(frame):
        fh, fw = frame.shape[:2]
        locations = []
        try:
            locations = face_recognition.face_locations(frame, number_of_times_to_upsample=1)
            if len(locations) == 0:
                locations = face_recognition.face_locations(frame, number_of_times_to_upsample=2)
        except Exception as e:
            print(f"[AI] face_locations error: {e}")

        # Haar cascade fallback directly on full frame
        if len(locations) == 0:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(25, 25))
                if len(faces) == 0:
                    alt2_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
                    if os.path.exists(alt2_path):
                        cascade_alt2 = cv2.CascadeClassifier(alt2_path)
                        faces = cascade_alt2.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(25, 25))

                for (fx, fy, f_w, f_h) in faces:
                    pad_w = int(f_w * 0.15)
                    pad_h = int(f_h * 0.15)
                    top = max(0, fy - pad_h)
                    left = max(0, fx - pad_w)
                    bottom = min(fh, fy + f_h + pad_h)
                    right = min(fw, fx + f_w + pad_w)
                    locations.append((top, right, bottom, left))
            except Exception as e:
                print(f"[AI] Haar fallback note: {e}")

        if len(locations) == 0:
            return []

        # Deduplicate overlapping locations
        cleaned_locations = []
        for loc in locations:
            top, right, bottom, left = loc
            overlap = False
            for c_top, c_right, c_bottom, c_left in cleaned_locations:
                dx = min(right, c_right) - max(left, c_left)
                dy = min(bottom, c_bottom) - max(top, c_top)
                if dx > 0 and dy > 0:
                    area_inter = dx * dy
                    area_a = (right - left) * (bottom - top)
                    if area_inter / max(1, area_a) > 0.45:
                        overlap = True
                        break
            if not overlap:
                cleaned_locations.append(loc)

        # Process each detected face location individually to prevent one edge-case box from discarding others
        results = []
        for loc in cleaned_locations:
            top, right, bottom, left = loc
            bbox = (int(left), int(top), int(right - left), int(bottom - top))
            enc = None
            try:
                encs = face_recognition.face_encodings(frame, known_face_locations=[loc])
                if len(encs) > 0:
                    enc = encs[0].astype(np.float32).tolist()
            except Exception as e:
                pass

            # Fallback to cropped patch embedding with full 68-point dlib context
            if not enc:
                try:
                    crop = crop_and_preprocess_face(frame, bbox)
                    if crop is not None:
                        enc = generate_embedding(crop)
                except Exception:
                    pass

            if enc and len(enc) == 128:
                results.append((bbox, enc))

        return results

    # 1. Try standard orientation
    results = _extract_from_frame(img_rgb)
    if len(results) > 0:
        return results

    # 2. Try camera rotations (90° CW, 270° CW, 180°) in case EXIF was stripped by mobile browser/app
    for rot in (cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180):
        try:
            rotated = cv2.rotate(img_rgb, rot)
            rotated = ensure_8bit_rgb(rotated)
            rot_results = _extract_from_frame(rotated)
            if len(rot_results) > 0:
                print(f"[AI] Successfully detected {len(rot_results)} face(s) after camera rotation correction!")
                return rot_results
        except Exception:
            pass

    return []


def detect_all_faces(img_rgb):
    """
    Independent Multi-Scale Face Detector using OpenCV Haar Cascades
    (Frontal Default, Frontal Alt2, and Profile) with CLAHE illumination enhancement.
    Returns list of (x, y, w, h) bounding box tuples.
    """
    img_rgb = ensure_8bit_rgb(img_rgb)
    if img_rgb is None or img_rgb.size == 0 or img_rgb.shape[0] < 20 or img_rgb.shape[1] < 20:
        return []

    try:
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        try:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        except Exception:
            pass

        all_bboxes = []
        for cascade_name in ('haarcascade_frontalface_default.xml', 'haarcascade_frontalface_alt2.xml', 'haarcascade_profileface.xml'):
            path = cv2.data.haarcascades + cascade_name
            if os.path.exists(path):
                cascade = cv2.CascadeClassifier(path)
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(25, 25))
                for (x, y, w, h) in faces:
                    all_bboxes.append((int(x), int(y), int(w), int(h)))

        # Deduplicate overlapping boxes
        deduped = []
        for b in all_bboxes:
            bx, by, bw, bh = b
            overlap = False
            for dx, dy, dw, dh in deduped:
                inter_x = max(0, min(bx + bw, dx + dw) - max(bx, dx))
                inter_y = max(0, min(by + bh, dy + dh) - max(by, dy))
                if inter_x * inter_y > 0.40 * (bw * bh):
                    overlap = True
                    break
            if not overlap:
                deduped.append(b)

        return deduped
    except Exception as e:
        print(f"[AI] detect_all_faces error: {e}")
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
    Handles JSON string, float array, or nested multi-vector array safely.
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

    a = np.array(emb1, dtype=np.float32).reshape(-1)
    b = np.array(emb2, dtype=np.float32).reshape(-1)

    if a.size == 0 or b.size == 0:
        return 999.0

    if a.shape[0] == 128 and b.shape[0] == 128:
        return float(np.linalg.norm(a - b))

    # If b is a matrix of multiple vectors (N*128), calculate min distance against each 128-D angle
    if a.shape[0] == 128 and b.shape[0] % 128 == 0 and b.shape[0] > 128:
        vectors = b.reshape(-1, 128)
        dists = [float(np.linalg.norm(a - v)) for v in vectors]
        return min(dists) if dists else 999.0

    # Fallback to general norm
    min_len = min(a.shape[0], b.shape[0])
    if min_len >= 128:
        return float(np.linalg.norm(a[:128] - b[:128]))

    return 999.0


def match_face_to_students(query_embedding, class_students, threshold=MATCH_THRESHOLD):
    """
    Compares query_embedding against enrolled class students using face_recognition distance.
    Returns (best_student_user, best_distance, confidence_score, closest_student_user, candidate_scores)
    """
    if not query_embedding:
        return None, 999.0, 0.0, None, []

    best_student = None
    best_distance = float('inf')
    candidate_scores = []

    for student in class_students:
        emb = student.face_embedding
        st_name = f"{student.first_name} {student.last_name}".strip() or student.username
        if not emb:
            candidate_scores.append({
                'student_id': student.id,
                'username': student.username,
                'name': st_name,
                'distance': 999.0,
                'has_embedding': False
            })
            continue

        try:
            # Handle JSON string representation safely
            if isinstance(emb, str):
                import json
                try:
                    emb = json.loads(emb)
                except Exception:
                    pass

            # Multi-angle biometric bank support: if emb is a list of embeddings [[...], [...]]
            if isinstance(emb, list) and len(emb) > 0 and isinstance(emb[0], list):
                dist = min(euclidean_distance(query_embedding, single_emb) for single_emb in emb if single_emb)
            else:
                dist = euclidean_distance(query_embedding, emb)

            dist_rounded = round(float(dist), 4)
            candidate_scores.append({
                'student_id': student.id,
                'username': student.username,
                'name': st_name,
                'distance': dist_rounded,
                'has_embedding': True
            })

            if dist < best_distance:
                best_distance = dist
                best_student = student
        except Exception as e:
            print(f"[AI] Distance error for {student.username}: {e}")

    candidate_scores.sort(key=lambda c: c['distance'])

    if best_student and best_distance < threshold:
        confidence = round(float(1.0 - (best_distance / threshold)), 4)
        print(f"[AI MATCH] Recognized: {best_student.username} (dist: {best_distance:.4f}, conf: {confidence:.2f})")
        return best_student, round(best_distance, 4), max(0.0, confidence), best_student, candidate_scores

    closest_dist = round(best_distance, 4) if best_distance != float('inf') else 999.0
    print(f"[AI UNMATCHED] Closest face was {best_student.username if best_student else 'None'} at dist {closest_dist:.4f} (threshold: {threshold})")
    return None, closest_dist, 0.0, best_student, candidate_scores


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

        # Fallback if primary extraction found 0 faces
        if len(face_data) == 0:
            bboxes = detect_all_faces(img)
            for bbox in bboxes:
                crop = crop_and_preprocess_face(img, bbox)
                if crop is not None:
                    emb = generate_embedding(crop)
                    if emb:
                        face_data.append((bbox, emb))

        # Update total faces detected AFTER all extraction stages
        total_faces_detected += len(face_data)

        if progress_callback:
            try:
                progress_callback(idx + 1, len(photo_bytes_list), len(face_data))
            except Exception:
                pass

        for bbox, embedding in face_data:
            matched_student, dist, conf, closest_st, candidate_scores = match_face_to_students(embedding, class_students, threshold=threshold)

            if matched_student:
                present_student_ids.add(matched_student.id)
                match_details.append({
                    'photo_index': idx + 1,
                    'student_id': matched_student.id,
                    'student_name': f"{matched_student.first_name} {matched_student.last_name}".strip() or matched_student.username,
                    'roll_number': matched_student.roll_number,
                    'distance': dist,
                    'confidence': conf,
                    'candidate_scores': candidate_scores,
                    'embedding': embedding
                })
            else:
                unmatched_faces_count += 1
                closest_name = f"{closest_st.first_name} {closest_st.last_name}".strip() if closest_st else "None"
                closest_id = closest_st.id if closest_st else None
                match_details.append({
                    'photo_index': idx + 1,
                    'student_id': None,
                    'student_name': "Unmatched Face",
                    'roll_number': None,
                    'distance': dist,
                    'closest_candidate': closest_name,
                    'closest_candidate_id': closest_id,
                    'confidence': 0.0,
                    'candidate_scores': candidate_scores,
                    'embedding': embedding
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
