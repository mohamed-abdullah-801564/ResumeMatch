# AI Resume Match Checker

## Overview

This is a Streamlit web application that provides AI-powered resume matching analysis. The application allows users to upload their resume and job description (either as files or text input) to receive intelligent matching insights. The system is designed to help job seekers understand how well their resume aligns with specific job requirements.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **Layout**: Two-column design for side-by-side resume and job description input
- **File Upload**: Supports PDF and DOCX formats for both resume and job description
- **Input Flexibility**: Dual input method for job descriptions (file upload or direct text paste)
- **User Experience**: Clean, intuitive interface with success indicators and help text

### File Processing System
- **Text Extraction**: Modular utility system for extracting text from documents
- **Supported Formats**: PDF (via PyPDF2) and DOCX (via python-docx) processing
- **File Validation**: Type checking to ensure only supported file formats are processed
- **Error Handling**: Structured exception handling for file processing operations

### Code Organization
- **Separation of Concerns**: Main application logic separated from utility functions
- **Modular Design**: File processing utilities isolated in dedicated module
- **Type Safety**: Python type hints for better code maintainability

### Data Flow
1. User uploads resume file (PDF/DOCX) or pastes text
2. User provides job description via file upload or text input
3. Files are validated for correct format
4. Text content is extracted from uploaded documents
5. Extracted content is processed through NLP analysis for intelligent matching

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework for the user interface
- **PyPDF2**: PDF text extraction and processing
- **python-docx**: Microsoft Word document processing
- **spacy**: Natural language processing library for keyword extraction and text analysis
- **scikit-learn**: Machine learning library for NLP preprocessing support
- **io**: Built-in library for handling byte streams

### NLP Models
- **en_core_web_sm**: English language model for spaCy NLP processing

### File Format Support
- **PDF**: Document text extraction via PyPDF2
- **DOCX**: Microsoft Word document processing via python-docx

### AI Integration (Implemented)
- **NLP Analysis Engine**: Implemented using spaCy for natural language processing
- **Keyword Extraction**: Automated extraction of technical skills, soft skills, and general keywords
- **Match Score Calculation**: Percentage-based scoring system comparing resume and job description keywords
- **Intelligent Suggestions**: AI-generated recommendations for resume improvement
- **Skills Categorization**: Automatic classification of technical vs soft skills