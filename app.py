import streamlit as st
import os
from utils.file_processor import extract_text_from_file, validate_file_type

def main():
    # Set page configuration
    st.set_page_config(
        page_title="AI Resume Match Checker",
        page_icon="📄",
        layout="wide"
    )
    
    # Main title
    st.title("AI Resume Match Checker")
    st.markdown("Upload your resume and job description to get AI-powered matching analysis")
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if resume_file is not None:
            st.success(f"Resume uploaded: {resume_file.name}")
    
    with col2:
        st.subheader("📋 Job Description")
        
        # Option to choose between file upload or text input
        input_method = st.radio(
            "Choose input method:",
            ["Upload File (PDF/DOCX)", "Paste Text"],
            horizontal=True
        )
        
        job_description_file = None
        job_description_text = None
        
        if input_method == "Upload File (PDF/DOCX)":
            job_description_file = st.file_uploader(
                "Upload Job Description (PDF or DOCX)",
                type=['pdf', 'docx'],
                help="Upload job description in PDF or DOCX format"
            )
            if job_description_file is not None:
                st.success(f"Job description uploaded: {job_description_file.name}")
        else:
            job_description_text = st.text_area(
                "Paste Job Description",
                height=200,
                placeholder="Paste the job description text here..."
            )
            if job_description_text:
                st.success(f"Job description text entered ({len(job_description_text)} characters)")
    
    # Submit button
    st.markdown("---")
    submit_button = st.button("🚀 Analyze Resume Match", type="primary", use_container_width=True)
    
    # Process submission
    if submit_button:
        # Validation
        errors = []
        
        if resume_file is None:
            errors.append("Please upload a resume file")
        
        if input_method == "Upload File (PDF/DOCX)" and job_description_file is None:
            errors.append("Please upload a job description file")
        elif input_method == "Paste Text" and not job_description_text:
            errors.append("Please paste the job description text")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Show processing indicator
            with st.spinner("Processing files and analyzing match..."):
                try:
                    # Extract text from resume
                    resume_text = extract_text_from_file(resume_file)
                    
                    # Extract text from job description
                    if input_method == "Upload File (PDF/DOCX)":
                        job_desc_text = extract_text_from_file(job_description_file)
                    else:
                        job_desc_text = job_description_text
                    
                    # Validate extracted text
                    if not resume_text or not resume_text.strip():
                        st.error("Could not extract text from resume file. Please check the file format and content.")
                        return
                    
                    if not job_desc_text or not job_desc_text.strip():
                        st.error("Could not extract text from job description. Please check the file format and content.")
                        return
                    
                    # Display results sections
                    st.markdown("---")
                    st.header("📊 Analysis Results")
                    
                    # Create columns for results
                    result_col1, result_col2 = st.columns([1, 2])
                    
                    with result_col1:
                        st.subheader("Resume Match Score")
                        
                        # Placeholder score display
                        score_placeholder = st.empty()
                        with score_placeholder.container():
                            st.metric(
                                label="Match Score",
                                value="Processing...",
                                help="AI-powered compatibility score between resume and job description"
                            )
                            st.info("🤖 AI analysis will be implemented here")
                    
                    with result_col2:
                        st.subheader("Suggestions")
                        
                        # Placeholder suggestions
                        suggestions_placeholder = st.empty()
                        with suggestions_placeholder.container():
                            st.info("📝 AI-generated suggestions will appear here")
                            st.markdown("""
                            **Placeholder suggestions:**
                            - Resume text extracted successfully ({} characters)
                            - Job description text extracted successfully ({} characters)
                            - AI matching algorithm integration pending
                            - Detailed recommendations will be provided once AI service is connected
                            """.format(len(resume_text), len(job_desc_text)))
                    
                    # Display extracted text for verification (in expander)
                    with st.expander("📄 View Extracted Text (for verification)", expanded=False):
                        col_resume, col_job = st.columns(2)
                        
                        with col_resume:
                            st.subheader("Resume Text")
                            st.text_area("Extracted Resume Content", resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text, height=200, disabled=True)
                        
                        with col_job:
                            st.subheader("Job Description Text")
                            st.text_area("Extracted Job Description Content", job_desc_text[:1000] + "..." if len(job_desc_text) > 1000 else job_desc_text, height=200, disabled=True)
                
                except Exception as e:
                    st.error(f"An error occurred while processing the files: {str(e)}")
                    st.error("Please check that your files are valid PDF or DOCX documents and try again.")

if __name__ == "__main__":
    main()
