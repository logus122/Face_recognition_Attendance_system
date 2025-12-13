# camera.py
import cv2
import os
import tempfile

def capture_from_camera(return_image=False):
    """
    Chụp ảnh từ camera.
    return_image=True: Trả về numpy array.
    return_image=False: Lưu file tạm và trả về đường dẫn.
    """
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return None

    print("Camera opened. Press SPACE to capture, ESC to cancel.")
    captured_image = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame")
            break

        cv2.imshow('Camera - Press SPACE to capture, ESC to cancel', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            captured_image = frame
            print("Image captured!")
            break
        if key == 27: # ESC
            print("Capture cancelled")
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_image is not None:
        if return_image:
            return captured_image
        else:
            temp_dir = tempfile.gettempdir()
            save_path = os.path.join(temp_dir, "captured_face.jpg")
            cv2.imwrite(save_path, captured_image)
            return save_path

    return None