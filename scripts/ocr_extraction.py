import cv2
import pytesseract
import os
import pandas as pd
import re

# Set the path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

aadhaar_pattern = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')
dob_pattern = re.compile(r'\b\d{2}[-/]\d{2}[-/]\d{4}\b')

def extract_fields_from_image(img_path: str):
    """Run OCR on a single image and return structured info."""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    aadhaar_match = aadhaar_pattern.search(text)
    dob_match = dob_pattern.search(text)

    aadhaar_number = aadhaar_match.group() if aadhaar_match else "Not Found"
    dob = dob_match.group() if dob_match else "Not Found"

    lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 2]
    name = lines[0] if lines else "Not Found"

    return {
        "Filename": os.path.basename(img_path),
        "Name": name,
        "DOB": dob,
        "AadhaarNumber": aadhaar_number,
        "raw_text": text,
    }

if __name__ == "__main__":
    # Input (preprocessed Aadhaar images) and output folders
    INPUT_DIR = "data/preprocessed/"
    OUTPUT_DIR = "outputs/"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = []

    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {file}...")
            img_path = os.path.join(INPUT_DIR, file)

            result = extract_fields_from_image(img_path)
            data.append({
                "Filename": result["Filename"],
                "Name": result["Name"],
                "DOB": result["DOB"],
                "AadhaarNumber": result["AadhaarNumber"],
            })

            # save raw text per file
            with open(os.path.join(OUTPUT_DIR, f"{file}.txt"), "w", encoding="utf-8") as f:
                f.write(result["raw_text"])

    df = pd.DataFrame(data)
    df.to_csv(os.path.join(OUTPUT_DIR, "ocr_results.csv"), index=False)

    print("\n✅ OCR Extraction Completed Successfully!")
    print("Results saved in outputs/ocr_results.csv")
