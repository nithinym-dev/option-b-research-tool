import pdfplumber
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract
import os
import re

MAX_FILE_SIZE_MB = 20
MAX_TEXT_LENGTH = 15000

def _truncate_text(text):
    """Truncate text safely for LLM processing"""
    if len(text) > MAX_TEXT_LENGTH:
        return text[:MAX_TEXT_LENGTH] + "\n\n[Text truncated due to length]"
    return text.strip()

def _clean_extracted_text(text):
    """Clean common PDF extraction artifacts"""
    # Remove excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Fix common encoding issues in Indian PDFs
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl').replace('ﬀ', 'ff')
    return text

def _extract_with_pdfminer(pdf_path):
    """Most tolerant extractor - handles corrupted PDFs best"""
    try:
        text = pdfminer_extract(pdf_path, maxpages=10)  # Limit to 10 pages for speed
        if text.strip():
            return True, _clean_extracted_text(text)
        return False, "No text extracted (pdfminer)"
    except Exception as e:
        return False, f"pdfminer error: {str(e)[:100]}"

def _extract_with_pdfplumber(pdf_path):
    """Try pdfplumber with relaxed settings"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages[:10]):  # First 10 pages only
                try:
                    # Try layout extraction first (more robust for tables)
                    page_text = page.extract_text(layout=True)
                    if not page_text or len(page_text.strip()) < 10:
                        # Fallback to simple extraction
                        page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text += f"\n\n--- Page {page_num + 1} ---\n\n" + page_text
                except Exception:
                    continue  # Skip problematic pages
        if text.strip():
            return True, _clean_extracted_text(text)
        return False, "No text extracted (pdfplumber)"
    except Exception as e:
        return False, f"pdfplumber error: {str(e)[:100]}"

def _extract_with_pypdf2(pdf_path):
    """Fallback with PyPDF2 (skip bad pages)"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file, strict=False)  # Critical: strict=False skips bad objects
            for page_num in range(min(10, len(reader.pages))):
                try:
                    page_text = reader.pages[page_num].extract_text()
                    if page_text and page_text.strip():
                        text += f"\n\n--- Page {page_num + 1} ---\n\n" + page_text
                except Exception:
                    continue
        if text.strip():
            return True, _clean_extracted_text(text)
        return False, "No text extracted (PyPDF2)"
    except Exception as e:
        return False, f"PyPDF2 error: {str(e)[:100]}"

def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF using multiple tolerant strategies.
    Works for problematic Indian financial PDFs.
    
    Returns:
        (success: bool, text_or_error: str)
    """
    try:
        if not os.path.exists(pdf_path):
            return False, "File not found"

        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB allowed."

        # Strategy 1: pdfminer.six (most tolerant for corrupted PDFs)
        success, text = _extract_with_pdfminer(pdf_path)
        if success:
            return True, _truncate_text(text)
        
        # Strategy 2: pdfplumber with layout extraction
        success, text = _extract_with_pdfplumber(pdf_path)
        if success:
            return True, _truncate_text(text)
        
        # Strategy 3: PyPDF2 with strict=False
        success, text = _extract_with_pypdf2(pdf_path)
        if success:
            return True, _truncate_text(text)
        
        # Final fallback: Try raw text extraction
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read().decode('latin-1', errors='ignore')
                # Look for text patterns in raw bytes
                text_match = re.search(r'([A-Z][a-z]{3,}.*?){5,}', content[:50000])
                if text_match:
                    return True, _truncate_text(text_match.group(0)[:2000])
        except:
            pass

        return False, "No readable text could be extracted. PDF may have non-standard encoding."

    except Exception as e:
        return False, f"Extraction error: {str(e)}"

def extract_text_from_txt(txt_path):
    """Extract text from TXT file"""
    try:
        if not os.path.exists(txt_path):
            return False, "File not found"

        with open(txt_path, "r", encoding="utf-8", errors="ignore") as file:
            text = file.read()

        if not text.strip():
            return False, "Text file is empty"

        return True, _truncate_text(text)

    except Exception as e:
        return False, f"Error reading text file: {str(e)}"