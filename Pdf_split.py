import os
import PyPDF2
from pdf2image import convert_from_path
import pytesseract
import streamlit as st

# Set the path to the Tesseract executable (update this path based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'./Tesseract-OCR/tesseract.exe'  # Update this if needed

def extract_text_from_pdf(input_pdf):
    # Convert PDF to images
    images = convert_from_path(input_pdf, poppler_path=r"F:\ocr_rnd\poppler-24.08.0\Library\bin")
    text_pages = []

    for image in images:
        text = pytesseract.image_to_string(image)
        text_pages.append(text)

    return text_pages

def split_pdf(input_pdf):
    text_pages = extract_text_from_pdf(input_pdf)

    sleep_study_writer = PyPDF2.PdfWriter()
    insurance_writer = PyPDF2.PdfWriter()

    with open(input_pdf, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page_num, text in enumerate(text_pages):
            # Check for keywords to classify the page
            if "number" in text.lower():
                sleep_study_writer.add_page(reader.pages[page_num])
            elif "insurance" in text.lower():
                insurance_writer.add_page(reader.pages[page_num])

    return sleep_study_writer, insurance_writer

# Streamlit UI
st.title("PDF Splitter")
st.write("Upload your PDF containing sleep study and insurance details.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    input_pdf_path = f"temp_{uploaded_file.name}"
    with open(input_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Split PDF"):
        sleep_study_writer, insurance_writer = split_pdf(input_pdf_path)

        # Save the split PDF files
        sleep_study_file_path = "sleep_study.pdf"
        insurance_file_path = "insurance.pdf"

        with open(sleep_study_file_path, "wb") as sleep_file:
            sleep_study_writer.write(sleep_file)

        with open(insurance_file_path, "wb") as insurance_file:
            insurance_writer.write(insurance_file)

        st.success("PDF has been split successfully!")
        st.download_button("Download Sleep Study PDF", sleep_study_file_path)
        st.download_button("Download Insurance PDF", insurance_file_path)

    # Clean up the temporary file
    os.remove(input_pdf_path)
