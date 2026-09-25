import cv2
import requests
import json
import sys

SERVER_URL = "http://127.0.0.1:8000"
DEFAULT_PHONE_IP = "192.168.50.224:8080"

def main():
    print("\n==================================================")
    print("      LIVE CAMERA FACE RECOGNITION TESTER")
    print("==================================================")
    camera_input = input(f"Enter Phone IP Webcam URL/IP [Press Enter for Phone ({DEFAULT_PHONE_IP})]: ").strip()

    if not camera_input:
        camera_input = DEFAULT_PHONE_IP

    if camera_input == "0" or camera_input.lower() == "webcam":
        print("Connecting to Laptop Webcam...")
        cap = cv2.VideoCapture(0)
    else:
        if not camera_input.startswith("http"):
            stream_url = f"http://{camera_input}/video"
        else:
            stream_url = camera_input if camera_input.endswith("/video") else f"{camera_input}/video"
        print(f"Connecting to Phone IP Webcam stream: {stream_url}...")
        cap = cv2.VideoCapture(stream_url)

    if not cap.isOpened():
        print("ERROR: Could not open camera stream. Please check Wi-Fi connection/IP address.")
        return

    print("\n==================================================")
    print("  Controls:")
    print("   [SPACE] : Snap live photo & Process Attendance")
    print("   [ R ]   : Snap live photo & Register Student Face")
    print("   [ Q ]   : Quit")
    print("==================================================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from camera stream.")
            break

        # Render on-screen instructions overlay
        display = frame.copy()
        cv2.putText(display, "Press SPACE to Test Attendance | R to Register | Q to Quit",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Scale down display window for smooth preview if high-res
        h, w = display.shape[:2]
        if w > 1280:
            scale_percent = 1280.0 / w
            dim = (1280, int(h * scale_percent))
            preview = cv2.resize(display, dim, interpolation=cv2.INTER_AREA)
        else:
            preview = display

        cv2.imshow("Phone IP Webcam Live Attendance Test", preview)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q') or key == 27: # Q or ESC
            print("Exiting live camera test.")
            break

        elif key == 32: # SPACE BAR -> Test Attendance
            print("\n[Captured live frame] -> Sending to Attendance API...")
            _, img_encoded = cv2.imencode('.jpg', frame)
            files = {'photos': ('live_frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
            data = {'class_id': 1}

            try:
                res = requests.post(f"{SERVER_URL}/api/attendance/process-photos/", data=data, files=files)
                if res.status_code == 200:
                    result = res.json()
                    print("\n--- ATTENDANCE TEST RESULT ---")
                    print(f"   Total Faces Detected: {result['total_faces_detected']}")
                    print(f"   Present Count:        {result['present_count']}")
                    print(f"   Present Students:     {[s['name'] for s in result['present_students']]}")
                    print(f"   Absent Students:      {[s['name'] for s in result['absent_students']]}")
                    print("   Match Details:\n" + json.dumps(result['match_details'], indent=2))
                else:
                    print(f"ERROR {res.status_code}:", res.text)
            except Exception as e:
                print("Request failed. Is Django server running? Error:", e)

        elif key == ord('r') or key == ord('R'): # R -> Register Face
            student_id = input("\nEnter Student ID to register (e.g. 5 for Hammad, 6 for Ayush): ").strip()
            if student_id.isdigit():
                print(f"[Captured live frame] -> Registering for Student ID {student_id}...")
                _, img_encoded = cv2.imencode('.jpg', frame)
                files = {'photos': ('register_frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
                try:
                    res = requests.post(f"{SERVER_URL}/api/users/{student_id}/register-face/", files=files)
                    if res.status_code == 200:
                        print("Registration Success:", res.json()['message'])
                    else:
                        print("Registration Error:", res.text)
                except Exception as e:
                    print("Registration failed. Error:", e)
            else:
                print("Invalid Student ID entered.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
