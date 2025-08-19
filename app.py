import streamlit as st
import os
from datetime import datetime
import io

# Simple imports without complex dependencies first
try:
    from utils.file_processor import extract_text_from_file, validate_file_type
    from utils.nlp_analyzer import ResumeJobMatcher
    from utils.pdf_generator import ResumeAnalysisReportGenerator
    FULL_FEATURES = True
except ImportError as e:
    st.error(f"Import error: {e}")
    FULL_FEATURES = False

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
    
    if not FULL_FEATURES:
        st.error("Some features are not available due to import issues. Please check the logs.")
        return
    
    # Initialize the NLP matcher
    @st.cache_resource
    def load_nlp_matcher():
        try:
            return ResumeJobMatcher()
        except Exception as e:
            st.error(f"Failed to load NLP matcher: {e}")
            return None
    
    matcher = load_nlp_matcher()
    if not matcher:
        st.error("Failed to initialize the matching system. Please refresh the page.")
        return
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your resume in PDF or DOCX format"
        )
        
        # Show resume preview
        if resume_file is not None:
            try:
                if validate_file_type(resume_file, ['pdf', 'docx']):
                    resume_text = extract_text_from_file(resume_file)
                    if resume_text:
                        st.success("✅ Resume loaded successfully!")
                        with st.expander("Preview Resume Text"):
                            st.text_area("Resume Content", resume_text[:500] + "..." if len(resume_text) > 500 else resume_text, height=150)
                    else:
                        st.error("Could not extract text from resume. Please check the file.")
                else:
                    st.error("Invalid file type. Please upload PDF or DOCX files only.")
            except Exception as e:
                st.error(f"Error processing resume: {e}")

    with col2:
        st.subheader("📋 Job Description")
        
        # Option to upload file or paste text
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Text"],
            horizontal=True
        )
        
        job_text = ""
        
        if input_method == "Upload File":
            job_file = st.file_uploader(
                "Upload Job Description (PDF or DOCX)",
                type=['pdf', 'docx'],
                help="Upload the job description in PDF or DOCX format"
            )
            
            if job_file is not None:
                try:
                    if validate_file_type(job_file, ['pdf', 'docx']):
                        job_text = extract_text_from_file(job_file)
                        if job_text:
                            st.success("✅ Job description loaded successfully!")
                            with st.expander("Preview Job Description"):
                                st.text_area("Job Description", job_text[:500] + "..." if len(job_text) > 500 else job_text, height=150)
                        else:
                            st.error("Could not extract text from job description.")
                    else:
                        st.error("Invalid file type. Please upload PDF or DOCX files only.")
                except Exception as e:
                    st.error(f"Error processing job description: {e}")
        
        else:  # Paste Text
            job_text = st.text_area(
                "Paste Job Description",
                height=200,
                placeholder="Paste the job description here..."
            )
            if job_text:
                st.success("✅ Job description text received!")

    # Analysis section
    st.markdown("---")
    
    # Submit button
    if st.button("🚀 Analyze Resume Match", type="primary", use_container_width=True):
        if resume_file is not None and job_text:
            try:
                # Get resume text
                resume_text = extract_text_from_file(resume_file)
                
                if not resume_text or not job_text:
                    st.error("Could not extract text from one or both files. Please try again.")
                    return
                
                # Perform analysis
                with st.spinner("Analyzing resume match..."):
                    analysis_result = matcher.calculate_match_score(resume_text, job_text)
                
                # Display results
                st.success("Analysis completed!")
                
                # Overall score
                overall_score = analysis_result.get('overall_score', analysis_result['keyword_score'])
                st.metric("Overall Match Score", f"{overall_score:.1f}%")
                
                # Detailed scores
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Keyword Match", f"{analysis_result['keyword_score']:.1f}%")
                with col2:
                    st.metric("Technical Skills", f"{analysis_result['technical_score']:.1f}%")
                with col3:
                    st.metric("Soft Skills", f"{analysis_result['soft_skills_score']:.1f}%")
                
                # Semantic analysis if available
                if analysis_result.get('semantic_score', 0) > 0:
                    st.subheader("🧠 Semantic Analysis")
                    st.metric("Semantic Similarity", f"{analysis_result['semantic_score']:.1f}%")
                
                # Missing skills
                st.subheader("❌ Missing Skills")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Technical Skills:**")
                    if analysis_result['missing']['technical']:
                        for skill in list(analysis_result['missing']['technical'])[:5]:
                            st.write(f"• {skill}")
                    else:
                        st.write("✅ All technical skills covered")
                
                with col2:
                    st.write("**Soft Skills:**")
                    if analysis_result['missing']['soft_skills']:
                        for skill in list(analysis_result['missing']['soft_skills'])[:5]:
                            st.write(f"• {skill}")
                    else:
                        st.write("✅ All soft skills covered")
                
                # Basic suggestions
                st.subheader("💡 Improvement Suggestions")
                suggestions = []
                
                if overall_score < 30:
                    suggestions.append("Your resume needs significant improvement to match this job description. Consider adding more relevant keywords and skills.")
                elif overall_score < 60:
                    suggestions.append("Good foundation, but there's room for improvement. Focus on adding missing technical skills.")
                elif overall_score < 80:
                    suggestions.append("Strong match! Consider fine-tuning a few areas to make your resume even more competitive.")
                else:
                    suggestions.append("Excellent match! Your resume aligns very well with this job description.")
                
                if analysis_result['missing']['technical']:
                    missing_tech = list(analysis_result['missing']['technical'])[:3]
                    suggestions.append(f"Consider adding these technical skills: {', '.join(missing_tech)}")
                
                if analysis_result['missing']['soft_skills']:
                    missing_soft = list(analysis_result['missing']['soft_skills'])[:2]
                    suggestions.append(f"Highlight these soft skills: {', '.join(missing_soft)}")
                
                for i, suggestion in enumerate(suggestions[:5], 1):
                    st.write(f"{i}. {suggestion}")
                
                # PDF Report Generation
                st.subheader("📊 Download Report")
                try:
                    report_generator = ResumeAnalysisReportGenerator()
                    pdf_buffer = report_generator.generate_report(
                        analysis_result,
                        suggestions
                    )
                    
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Could not generate PDF report: {e}")
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.write("Please try again or contact support if the issue persists.")
        
        else:
            st.warning("Please upload a resume and provide a job description before analyzing.")

if __name__ == "__main__":
    main()