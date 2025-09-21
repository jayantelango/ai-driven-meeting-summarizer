import PyPDF2
import docx
import io
import speech_recognition as sr
import pydub
from pydub import AudioSegment
import tempfile
import os

def text_from_pdf(file_stream):
    """Extract text content from PDF files"""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error reading PDF file: {str(e)}")

def text_from_docx(file_stream):
    """Extract text content from DOCX files"""
    try:
        doc = docx.Document(file_stream)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Error reading DOCX file: {str(e)}")

def text_from_txt(file_stream):
    """Extract text content from TXT files"""
    try:
        return file_stream.read().decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error reading TXT file: {str(e)}")

def text_from_audio(file_stream, filename):
    """Extract text content from audio files using speech recognition"""
    try:
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_stream.read())
            temp_file_path = temp_file.name
        
        try:
            # Convert audio to WAV format for better recognition
            audio = AudioSegment.from_file(temp_file_path)
            
            # Convert to mono and set sample rate
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Export as WAV
            wav_path = temp_file_path.replace(os.path.splitext(temp_file_path)[1], '.wav')
            audio.export(wav_path, format="wav")
            
            # Initialize speech recognition
            recognizer = sr.Recognizer()
            
            # Use Google Speech Recognition
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            
            # Perform speech recognition
            try:
                text = recognizer.recognize_google(audio_data, language='en-US')
                return text
            except sr.UnknownValueError:
                return "Could not understand the audio. Please ensure clear speech and try again."
            except sr.RequestError as e:
                return f"Speech recognition service error: {str(e)}"
                
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except Exception as e:
        raise ValueError(f"Error processing audio file: {str(e)}")

def process_file(file_stream, filename):
    """
    Process uploaded files and extract text content based on file type.
    
    Args:
        file_stream: File stream object
        filename: Name of the uploaded file
        
    Returns:
        str: Extracted text content
        
    Raises:
        ValueError: If file type is unsupported or processing fails
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return text_from_pdf(file_stream)
    elif filename_lower.endswith('.docx'):
        return text_from_docx(file_stream)
    elif filename_lower.endswith('.txt'):
        return text_from_txt(file_stream)
    elif filename_lower.endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')):
        return text_from_audio(file_stream, filename)
    else:
        raise ValueError(f"Unsupported file type: {filename}")