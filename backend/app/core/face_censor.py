import cv2
import numpy as np
import os

import sys

# MediaPipe imports
try:
    import mediapipe as mp
    
    # Check if we need to explicitly import solutions (sometimes needed in newer versions/docker)
    if not hasattr(mp, 'solutions'):
        try:
            import mediapipe.python.solutions as solutions
            mp.solutions = solutions
        except ImportError:
            pass

    mp_face_mesh = mp.solutions.face_mesh
    FaceMesh = mp_face_mesh.FaceMesh
except Exception as e:
    print(f"⚠️ Error initializing MediaPipe standard import: {e}", file=sys.stderr)
    try:
        # Fallback for some environments
        from mediapipe.python.solutions import face_mesh
        mp_face_mesh = face_mesh
        FaceMesh = face_mesh.FaceMesh
    except Exception as e2:
        print(f"❌ CRITICAL: Could not import MediaPipe: {e2}", file=sys.stderr)
        raise e2

class FaceCensor:
    """
    Face censorship using MediaPipe FaceMesh.
    Adapted from Tesis 1.0 for API use (no GUI/camera features).
    """
    
    def __init__(self, mode="blur", blur_strength=55, expand=10, pixel_size=10, cut=False):
        """
        Initialize FaceCensor.
        
        Parameters:
            mode: str -> censorship type ("blur", "black", or "pixelate")
            blur_strength: int -> blur intensity (for blur mode)
            expand: int -> expansion of censored area around eyes/mouth
            pixel_size: int -> pixel size (for pixelate mode)
            cut: bool -> if True, crop final image to detected face area
        """
        self.mode = mode
        self.blur_strength = blur_strength
        self.expand = expand
        self.pixel_size = pixel_size
        self.cut = cut

        # Initialize MediaPipe FaceMesh
        self.face_mesh = FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Landmark indices for targeted censorship
        self.LEFT_EYE = [33, 133]
        self.RIGHT_EYE = [362, 263]
        self.MOUTH = [78, 308, 14, 13]

    def _validate_resolution(self, width, height, min_width=1280, min_height=720):
        """
        Verify if content resolution is sufficient for processing.
        Default requires at least HD (1280x720).
        """
        width = int(width)
        height = int(height)

        # Relaxed validation: ensure total pixels are at least HD (1280x720 = 921,600 pixels)
        # This allows portrait images like 798x1200 (957,600 pixels) to pass.
        min_pixels = min_width * min_height
        current_pixels = width * height

        if current_pixels < min_pixels:
            print(f"⚠️ Warning: resolution too low ({width}x{height} = {current_pixels}px). "
                f"Requires at least {min_pixels}px (approx 720p) for proper processing.")
            return False
        else:
            print(f"✅ Valid resolution: {width}x{height}")
            return True

    def _get_box(self, points):
        """Returns bounding box coordinates for given points."""
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def _apply_censor(self, image, points):
        """
        Apply selected censorship type to the corresponding area.
        Returns (modified_image, (x1,y1,x2,y2) or None if no region).
        """
        x1, y1, x2, y2 = self._get_box(points)

        # Expand censored area according to "expand" parameter
        x1 = max(x1 - self.expand, 0)
        y1 = max(y1 - self.expand, 0)
        x2 = min(x2 + self.expand, image.shape[1])
        y2 = min(y2 + self.expand, image.shape[0])

        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return image, None

        # Apply chosen censorship type
        if self.mode == "blur":
            # blur_strength must be odd and reasonably large
            k = self.blur_strength if self.blur_strength % 2 == 1 else self.blur_strength + 1
            roi = cv2.GaussianBlur(roi, (k, k), 30)

        elif self.mode == "black":
            roi[:] = (0, 0, 0)

        elif self.mode == "pixelate":
            h, w = roi.shape[:2]
            # avoid pixel_size > min(h,w)
            px = max(1, min(self.pixel_size, min(h, w)))
            roi_small = cv2.resize(roi, (px, px), interpolation=cv2.INTER_LINEAR)
            roi = cv2.resize(roi_small, (w, h), interpolation=cv2.INTER_NEAREST)

        image[y1:y2, x1:x2] = roi
        return image, (x1, y1, x2, y2)

    def _process_frame(self, frame):
        """
        Process a frame and apply censorship to eyes and mouth.
        If cut=True, crop image to full face bounding box (using all landmarks).
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame

        h, w, _ = frame.shape
        final_box = None

        for face_landmarks in results.multi_face_landmarks:
            # List with all face points (x,y)
            landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in face_landmarks.landmark]

            # 1) Determine full face box using all landmarks
            fx1, fy1, fx2, fy2 = self._get_box(landmarks)
            # expand full face box with same expand parameter
            fx1 = max(fx1 - self.expand, 0)
            fy1 = max(fy1 - self.expand, 0)
            fx2 = min(fx2 + self.expand, frame.shape[1])
            fy2 = min(fy2 + self.expand, frame.shape[0])
            final_box = (fx1, fy1, fx2, fy2)

            # 2) Apply targeted censorship (eyes and mouth)
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.LEFT_EYE])
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.RIGHT_EYE])
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.MOUTH])

            # (using max_num_faces=1 by default)
            break

        # 3) If cut requested, crop to full face box
        if self.cut and final_box:
            x1, y1, x2, y2 = final_box
            # Ensure integers and valid limits
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
            # Avoid empty crop
            if x2 > x1 and y2 > y1:
                frame = frame[y1:y2, x1:x2]

        return frame

    def process_image(self, input_path, output_path=None):
        """
        Process an image file applying censorship (and optional crop).
        Returns processed image as numpy array or None if failed.
        """
        image = cv2.imread(input_path)
        if image is None:
            print(f"❌ Could not read image: {input_path}")
            return None
        
        h, w = image.shape[:2]

        # ⚠️ Resolution validation
        if not self._validate_resolution(w, h):
            print("🚫 Image rejected due to low resolution.")
            return None

        result = self._process_frame(image)

        if output_path:
            # Create folder if doesn't exist
            folder = os.path.dirname(output_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
                print(f"📁 Folder created: {folder}")

            # Save image
            cv2.imwrite(output_path, result)
            print(f"💾 Censored image saved at: {output_path}")

        return result