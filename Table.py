import pdfplumber
import pytesseract
import cv2
import numpy as np
from PIL import Image
import pandas as pd

# Set up Tesseract path if necessary
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image_for_ocr(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply binary thresholding
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Deskew if necessary
    return binary

def extract_text_from_image(image):
    # Run Tesseract OCR on the processed image
    return pytesseract.image_to_string(image, config='--psm 6')  # --psm 6 for complex layouts

def extract_tables_and_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []
        all_texts = []
        
        for page_number, page in enumerate(pdf.pages):
            print(f"Processing page {page_number + 1}")
            
            # Extract tables using pdfplumber
            tables = page.extract_tables()
            for table in tables:
                if table:  # Only add non-empty tables
                    table_data = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append((page_number + 1, table_data))  # Store page number with table

            # Convert page to image for OCR of non-table content
            pil_image = page.to_image(resolution=300).original
            open_cv_image = np.array(pil_image)
            open_cv_image = open_cv_image[:, :, ::-1].copy()  # Convert RGB to BGR
            
            # Preprocess the image for better OCR results
            processed_image = preprocess_image_for_ocr(open_cv_image)
            pil_image_for_ocr = Image.fromarray(processed_image)
            
            # Extract text with OCR
            page_text = extract_text_from_image(pil_image_for_ocr)
            all_texts.append((page_number + 1, page_text))
            
            # Print OCR output for each page (optional)
            print(f"OCR Text for page {page_number + 1}:\n{page_text}\n")
        
        return all_tables, all_texts

def structure_and_save_output(tables, texts):
    # Save tables to Excel file with sheet names indicating page number
    with pd.ExcelWriter("extracted_tables.xlsx") as writer:
        for page_num, table_data in tables:
            sheet_name = f'Page_{page_num}_Table'
            table_data.to_excel(writer, sheet_name=sheet_name, index=False)

    # Save OCR text to a text file, organized by page
    with open("extracted_texts.txt", "w") as text_file:
        for page_num, text in texts:
            text_file.write(f"Page {page_num}:\n{text}\n\n")

# Run the extraction and save results
pdf_path = "your_file.pdf"
tables, texts = extract_tables_and_text_from_pdf(pdf_path)
structure_and_save_output(tables, texts)
