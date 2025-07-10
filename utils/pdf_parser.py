from PyPDF2 import PdfReader

def parse_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# Alias for compatibility
extract_text_from_pdf = parse_pdf
