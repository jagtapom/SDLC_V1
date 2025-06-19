# import os
# import docx2txt
# import pdfplumber

# def extract_text(file_path: str, keyword: str = None) -> str:
#     ext = os.path.splitext(file_path)[1].lower()
#     if ext == '.pdf':
#         return extract_from_pdf(file_path, keyword)
#     elif ext == '.docx':
#         return extract_from_docx(file_path, keyword)
#     elif ext == '.txt':
#         return extract_from_txt(file_path, keyword)
#     else:
#         raise ValueError("Unsupported file format")

# def extract_from_pdf(file_path, keyword=None):
#     text = ""
#     with pdfplumber.open(file_path) as pdf:
#         for page in pdf.pages:
#             text += page.extract_text() or ""
#     return filter_text(text, keyword)

# def extract_from_docx(file_path, keyword=None):
#     text = docx2txt.process(file_path)
#     return filter_text(text, keyword)

# def extract_from_txt(file_path, keyword=None):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         text = f.read()
#     return filter_text(text, keyword)

# def filter_text(text, keyword):
#     if keyword:
#         lines = text.splitlines()
#         filtered = [line for line in lines if keyword.lower() in line.lower()]
#         return "\n".join(filtered)
#     return text
# document_processor.py

import fitz  # PyMuPDF

def extract_text(file_path: str, keyword: str = "") -> str:
    """
    Extracts text from PDF, DOCX, or TXT files.
    Filters by keyword if provided.
    """
    text = ""

    if file_path.lower().endswith(".pdf"):
        text = extract_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_from_docx(file_path)
    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    if keyword:
        # Return only sections containing the keyword
        filtered = [line for line in text.splitlines() if keyword.lower() in line.lower()]
        return "\n".join(filtered)

    return text

def extract_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    output = ""
    for page in doc:
        output += page.get_text()
    doc.close()
    return output

def extract_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
