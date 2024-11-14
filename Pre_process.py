import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_path, exceptions
import numpy as np
import cv2

# Set the path to the Tesseract executable for Windows users
pytesseract.pytesseract.tesseract_cmd = r'./Tesseract-OCR/tesseract.exe'

# Title of the app
st.title("PDF and Image OCR App with Noise Removal and Font Adjustment")

# File uploader for PDFs and images
uploaded_file = st.file_uploader("Upload PDF or Image (JPG/PNG)", type=["pdf", "jpg", "jpeg", "png"])

# Initialize an empty string to hold the combined OCR text
combined_text = ""

# Noise removal function
def noise_removal(img):
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    img = cv2.medianBlur(img, 3)
    return img

# Thin font function
def thin_font(img):
    img = cv2.bitwise_not(img)
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.bitwise_not(img)
    return img

# Thick font function
def thick_font(img):
    img = cv2.bitwise_not(img)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1)
    img = cv2.bitwise_not(img)
    return img

# Check if a file has been uploaded
if uploaded_file is not None:
    processing_option = st.selectbox("Choose Preprocessing Option", ["None", "Noise Removal", "Thin Font", "Thick Font"])

    # If the uploaded file is a PDF
    if uploaded_file.type == "application/pdf":
        try:
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Attempt to convert PDF to images
            images = convert_from_path("temp.pdf", 500, poppler_path=r'./poppler-24.08.0/Library/bin')

            for i, image in enumerate(images):
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                if processing_option == "Noise Removal":
                    image_cv = noise_removal(image_cv)
                elif processing_option == "Thin Font":
                    image_cv = thin_font(image_cv)
                elif processing_option == "Thick Font":
                    image_cv = thick_font(image_cv)

                ocr_text = pytesseract.image_to_string(image_cv)
                combined_text += ocr_text + "\n"

        except exceptions.PDFPageCountError:
            st.error("Error: Unable to read the PDF file. The file may be corrupted or have 0 pages.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        img = Image.open(uploaded_file)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        if processing_option == "Noise Removal":
            img_cv = noise_removal(img_cv)
        elif processing_option == "Thin Font":
            img_cv = thin_font(img_cv)
        elif processing_option == "Thick Font":
            img_cv = thick_font(img_cv)

        ocr_text = pytesseract.image_to_string(img_cv)
        combined_text += ocr_text + "\n"

    st.subheader("Extracted Text")
    st.write(combined_text)
else:
    st.write("Please upload a PDF or an image file to extract text.")
