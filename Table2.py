pip install pymupdf pytesseract opencv-python-headless streamlit


import streamlit as st
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
from PIL import Image

# Set up Tesseract path (only if Tesseract is not in your PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_images(pdf_file):
    """Converts each page of the PDF into an image."""
    doc = fitz.open("pdf", pdf_file.read())
    images = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def extract_tables_from_image(image):
    """Detects and extracts tables from an image."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 30
    )
    
    # Detect vertical and horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    
    # Detect horizontal lines
    horizontal_lines = cv2.erode(thresh, horizontal_kernel, iterations=1)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
    
    # Detect vertical lines
    vertical_lines = cv2.erode(thresh, vertical_kernel, iterations=1)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
    
    # Combine horizontal and vertical lines
    table_structure = cv2.add(horizontal_lines, vertical_lines)
    
    # Find contours in the table structure
    contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    tables = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 20:  # Filter out small boxes
            table_img = gray[y:y + h, x:x + w]
            tables.append(table_img)
    
    return tables

def extract_text_from_table(table_img):
    """Extracts text from the detected table using OCR."""
    return pytesseract.image_to_string(table_img, config='--psm 6')

# Streamlit app
st.title("PDF Table Extractor using OCR")

# Upload PDF
pdf_file = st.file_uploader("Upload a PDF file", type="pdf")
if pdf_file:
    st.write("Processing PDF...")
    images = pdf_to_images(pdf_file)
    
    # Process each page and extract tables
    for i, image in enumerate(images):
        st.write(f"Page {i + 1}")
        tables = extract_tables_from_image(image)
        
        if tables:
            for j, table_img in enumerate(tables):
                st.write(f"Table {j + 1}")
                
                # Display table image
                st.image(table_img, caption=f"Table {j + 1} Image", use_column_width=True)
                
                # Extract and display text
                table_text = extract_text_from_table(table_img)
                st.text(table_text)
        else:
            st.write("No tables detected on this page.")
