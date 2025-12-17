# scripts/integrated_pipeline.py
import os
import traceback
from pathlib import Path
import cv2
from typing import Dict, Any

# ultralytics YOLO import may be heavy; import lazily
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

from scripts.ocr_extraction import extract_fields_from_image

# Helper
def safe_percent(x: float) -> str:
    try:
        return f"{round(float(x) * 100, 1)}%"
    except Exception:
        return "0%"

class FraudEngine:
    def __init__(self,
                 detector_path: str = "models/detector.pt",
                 classifier_path: str = "models/classifier.pt"):
        self.detector_path = Path(detector_path)
        self.classifier_path = Path(classifier_path)

        # Try to load models only if ultralytics is available and files exist
        self.detector = None
        self.classifier = None

        if YOLO is None:
            print("⚠️ ultralytics not available. Detector/classifier will be disabled.")
        else:
            if self.detector_path.exists():
                try:
                    self.detector = YOLO(str(self.detector_path))
                    print(f"✅ Detector loaded from {self.detector_path}")
                except Exception as e:
                    print("❌ Failed to load detector:", e)
            else:
                print(f"⚠️ Detector file not found at {self.detector_path}")

            if self.classifier_path.exists():
                try:
                    self.classifier = YOLO(str(self.classifier_path))
                    print(f"✅ Classifier loaded from {self.classifier_path}")
                except Exception as e:
                    print("❌ Failed to load classifier:", e)
            else:
                print(f"⚠️ Classifier file not found at {self.classifier_path}")

    def _detect_and_crop(self, image_path: str) -> str:
        """Detect main document / face region and return path to cropped image.
           If detector not available or detection fails, return original image_path."""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"cv2 could not read image: {image_path}")

            if self.detector is None:
                # no detector available → return original
                print("⚠️ Detector missing, skipping crop.")
                return image_path

            results = self.detector(image_path, save=False)
            # results is ultralytics Results; ensure boxes exist
            r0 = results[0]
            boxes = getattr(r0, "boxes", None)
            if boxes is None or len(boxes) == 0:
                print("ℹ️ Detector found no boxes → returning original image.")
                return image_path

            # take first box
            xyxy = boxes.xyxy[0].tolist()  # [x1, y1, x2, y2]
            x1, y1, x2, y2 = map(int, xyxy)
            h, w = img.shape[:2]
            # clamp coords
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)
            if x2 <= x1 or y2 <= y1:
                print("⚠️ Invalid box, returning original.")
                return image_path

            crop = img[y1:y2, x1:x2]
            crop_path = "outputs/cropped_temp.jpg"
            os.makedirs("outputs", exist_ok=True)
            cv2.imwrite(crop_path, crop)
            print(f"✅ Cropped image saved to {crop_path}")
            return crop_path
        except Exception as e:
            print("❌ Exception in _detect_and_crop:", e)
            traceback.print_exc()
            return image_path

    def _classify_real_fake(self, image_path: str) -> Dict[str, Any]:
        """Classify a crop as real/fake. Returns structured dict.
           If classifier not available, returns Unknown with low confidence."""
        try:
            if self.classifier is None:
                print("⚠️ Classifier missing, returning Unknown.")
                return {"status": "Unknown", "confidence": "0%", "reason": "No classifier available"}

            preds = self.classifier(image_path, save=False)  # don't save by default
            # preds[0] should be a Results object; try to extract probabilities robustly
            r0 = preds[0]

            # Method 1: ultralytics v8: r0.probs (Tensor) or r0.probs.data
            probs = None
            if hasattr(r0, "probs") and r0.probs is not None:
                try:
                    # convert to list of floats
                    probs = r0.probs.cpu().numpy().tolist()
                except Exception:
                    try:
                        probs = r0.probs.data.tolist()
                    except Exception:
                        probs = None

            # Method 2: classification results sometimes in r0.boxes or r0.pred
            if probs is None:
                # attempt using r0.boxes.cls or r0.boxes.conf (less likely)
                try:
                    # some classifier returns .probs as a 2-dim array per image
                    # fall back to values in r0.probs if shaped differently
                    probs = []
                except Exception:
                    probs = None

            # if still None, treat as unknown
            if not probs:
                print("⚠️ Could not extract probs from classifier output. Returning Unknown.")
                return {"status": "Unknown", "confidence": "0%", "reason": "Classifier output parsing failed"}

            # Expect probs like [prob_fake, prob_real] or [prob_real, prob_fake] — detect ordering
            # We'll assume highest score indicates predicted class; find index of max
            max_idx = int(max(range(len(probs[0]) if isinstance(probs[0], (list, tuple)) else len(probs)),
                              key=lambda i: probs[0][i] if isinstance(probs[0], (list, tuple)) else probs[i]))
            # flatten if nested
            if isinstance(probs[0], (list, tuple)):
                prob_list = probs[0]
            else:
                prob_list = probs

            # predicted label = index of max
            pred_idx = int(prob_list.index(max(prob_list)))
            pred_conf = float(prob_list[pred_idx])

            # Decide label names: try to infer by checking classifier.names if available
            label_name = None
            if hasattr(self.classifier, "names") and isinstance(self.classifier.names, (list, dict)):
                names = self.classifier.names
                # names might be dict or list
                try:
                    label_name = names[pred_idx]
                except Exception:
                    label_name = None

            # If label_name exists and contains real/fake words use that, otherwise map idx
            if label_name:
                label = str(label_name).upper()
            else:
                # fallback mapping: if 2-class -> idx 1 = REAL else we will return index-based label
                if len(prob_list) == 2:
                    # heuristic: pick idx 1 as REAL if that yields larger numeric (common)
                    label = "REAL" if pred_idx == 1 else "FAKE"
                else:
                    label = f"CLASS_{pred_idx}"

            reason = f"Predicted {label} with index {pred_idx}"
            return {
                "status": "Genuine" if label.upper() in ("REAL", "GENUINE") else ("Fraud" if label.upper() in ("FAKE", "FORGED") else label),
                "confidence": safe_percent(pred_conf),
                "reason": reason
            }
        except Exception as e:
            print("❌ Exception in _classify_real_fake:", e)
            traceback.print_exc()
            return {"status": "Unknown", "confidence": "0%", "reason": f"Error: {e}"}

    def predict(self, image_path: str) -> Dict[str, Any]:
        """Main pipeline. Returns consistent JSON expected by frontend."""
        try:
            image_path = str(Path(image_path))
            print(f"ℹ️ Predict called for: {image_path}")

            # Step A: detect and crop (if possible)
            crop_path = self._detect_and_crop(image_path)

            # Step B: classify real/fake on crop
            fraud_result = self._classify_real_fake(crop_path)

            # Step C: OCR (run on original image to capture full text)
            try:
                ocr_result = extract_fields_from_image(image_path)
            except Exception as e:
                print("❌ OCR extraction failed:", e)
                ocr_result = {"Filename": Path(image_path).name, "Name": "Not Found", "DOB": "Not Found", "AadhaarNumber": "Not Found", "raw_text": ""}

            # Normalize to frontend expected keys
            output = {
                "image_path": image_path,
                "crop_path": crop_path,
                "fraud": {
                    "status": fraud_result.get("status", "Unknown"),
                    "confidence": fraud_result.get("confidence", "0%"),
                    "reason": fraud_result.get("reason", "")
                },
                # frontend expects extracted_data
                "extracted_data": {
                    "name": ocr_result.get("Name") or ocr_result.get("name") or "Not Found",
                    "dob": ocr_result.get("DOB") or ocr_result.get("dob") or "Not Found",
                    "aadhaar_number": ocr_result.get("AadhaarNumber") or ocr_result.get("Aadhaar_Number") or "Not Found",
                    "raw_text": ocr_result.get("raw_text", "")
                }
            }

            print("✅ FINAL RESULT FROM BACKEND:")
            print(output)
            return output
        except Exception as e:
            print("❌ Exception in predict():", e)
            traceback.print_exc()
            return {
                "image_path": image_path,
                "crop_path": image_path,
                "fraud": {"status": "Unknown", "confidence": "0%", "reason": f"Error: {e}"},
                "extracted_data": {"name": "Not Found", "dob": "Not Found", "aadhaar_number": "Not Found", "raw_text": ""}
            }

# quick CLI test when run manually
if __name__ == "__main__":
    p = input("Image path: ")
    eng = FraudEngine()
    res = eng.predict(p)
    import json
    print(json.dumps(res, indent=2))
