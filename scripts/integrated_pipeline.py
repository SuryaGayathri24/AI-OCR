import os
from ultralytics import YOLO
import cv2
from pathlib import Path

from scripts.ocr_extraction import extract_fields_from_image

class FraudEngine:
    def __init__(self,
                 detector_path="models/detector.pt",
                 classifier_path="models/classifier.pt"):
        self.detector = YOLO(detector_path)
        self.classifier = YOLO(classifier_path)

    def _detect_and_crop(self, image_path: str) -> str:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        test_img = cv2.imread(image_path)
        if test_img is None:
            raise ValueError(f"Could not read image with cv2: {image_path}")

        det_result = self.detector(image_path, save=False)

        if len(det_result[0].boxes) == 0:
            # no detection → return original path
            return image_path

        box = det_result[0].boxes.xyxy[0].tolist()
        img = cv2.imread(image_path)
        x1, y1, x2, y2 = map(int, box)
        crop = img[y1:y2, x1:x2]

        crop_path = "outputs/cropped_temp.jpg"
        cv2.imwrite(crop_path, crop)
        return crop_path

    def _classify_real_fake(self, crop_path: str):
        pred = self.classifier(crop_path, save=True)
        probs = pred[0].probs.data.tolist()
        fake_score = probs[0]
        real_score = probs[1]

        label = "REAL" if real_score > fake_score else "FAKE"
        confidence = max(real_score, fake_score)

        return {
            "label": label,
            "confidence": float(confidence),
            "real_score": float(real_score),
            "fake_score": float(fake_score),
        }

    def predict(self, image_path: str):
        image_path = str(Path(image_path))
        crop_path = self._detect_and_crop(image_path)
        fraud_result = self._classify_real_fake(crop_path)
        ocr_result = extract_fields_from_image(image_path)

        return {
            "image_path": image_path,
            "crop_path": crop_path,
            "fraud": fraud_result,
            "ocr": ocr_result,
        }

# optional: keep CLI use
if __name__ == "__main__":
    img = input("Enter image path: ")
    engine = FraudEngine()
    result = engine.predict(img)
    print("\n===== FINAL RESULT =====")
    print(result)
