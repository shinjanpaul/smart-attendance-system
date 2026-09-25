import sys
import os
import cv2

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_engine import detect_all_faces, crop_and_preprocess_face, generate_embedding

def test_photo(image_path):
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' does not exist.")
        return

    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Unable to load image '{image_path}'.")
        return

    print(f"\n--- Testing Photo: {image_path} ---")
    faces = detect_all_faces(img)
    print(f"✅ Total Faces Detected: {len(faces)}")

    output_img = img.copy()
    for idx, (x, y, w, h) in enumerate(faces, 1):
        print(f"  Face #{idx}: Box = (x={x}, y={y}, w={w}, h={h})")
        # Crop & generate 128-D embedding to verify MobileFaceNet inference
        crop = crop_and_preprocess_face(img, (x, y, w, h))
        emb = generate_embedding(crop)
        print(f"    MobileFaceNet Embedding generated! Vector length: {len(emb)}")
        
        # Draw bounding box on output image
        cv2.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(output_img, f"Face #{idx}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    output_file = "face_detection_result.jpg"
    cv2.imwrite(output_file, output_img)
    print(f"📷 Result saved with bounding boxes to: {os.path.abspath(output_file)}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_photo(sys.argv[1])
    else:
        print("Usage: python test_face_detection.py <path_to_photo.jpg>")
