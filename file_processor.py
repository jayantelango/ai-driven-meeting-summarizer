import PyPDF2
import docx
import io

def text_from_pdf(file_stream):
    reader = PyPDF2.PdfReader(file_stream)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def text_from_docx(file_stream):
    doc = docx.Document(file_stream)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def text_from_txt(file_stream):
    return file_stream.read().decode('utf-8')

def process_file(file_stream, filename):
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return text_from_pdf(file_stream)
    elif filename_lower.endswith('.docx'):
        return text_from_docx(file_stream)
    elif filename_lower.endswith('.txt'):
        return text_from_txt(file_stream)
    elif filename_lower.endswith('.mp3'):
        return "Audio file transcription is a premium feature."
    else:
        raise ValueError(f"Unsupported file type: {filename}")
