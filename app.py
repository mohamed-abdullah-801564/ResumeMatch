import streamlit as st
import os
from utils.file_processor import extract_text_from_file, validate_file_type
from utils.nlp_analyzer import ResumeJobMatcher
from utils.pdf_generator import ResumeAnalysisReportGenerator
from datetime import datetime

def main():
    # Set page configuration
    st.set_page_config(
        page_title="AI Resume Match Checker",
        page_icon="📄",
        layout="wide"
    )
    
    # Initialize the NLP matcher
    @st.cache_resource
    def load_nlp_matcher():
        return ResumeJobMatcher()
    
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
                    
                    # Perform NLP analysis
                    matcher = load_nlp_matcher()
                    analysis_result = matcher.calculate_match_score(resume_text, job_desc_text)
                    suggestions = matcher.generate_suggestions(analysis_result)
                    
                    # Display results sections
                    st.markdown("---")
                    st.header("📊 Analysis Results")
                    
                    # Create columns for results
                    result_col1, result_col2 = st.columns([1, 2])
                    
                    with result_col1:
                        st.subheader("Resume Match Score")
                        
                        # Display actual match score
                        overall_score = analysis_result['overall_score']
                        
                        # Determine score color based on value
                        if overall_score >= 70:
                            score_color = "green"
                        elif overall_score >= 40:
                            score_color = "orange"
                        else:
                            score_color = "red"
                        
                        # Display main score
                        st.metric(
                            label="Overall Match Score",
                            value=f"{overall_score}%",
                            help="Percentage of job description keywords found in your resume"
                        )
                        
                        # Display detailed scores
                        st.markdown("**Detailed Breakdown:**")
                        st.write(f"🔧 Technical Skills: {analysis_result['technical_score']}%")
                        st.write(f"💼 Soft Skills: {analysis_result['soft_skills_score']}%")
                        st.write(f"📝 Keywords Matched: {analysis_result['total_matches']}/{analysis_result['total_job_keywords']}")
                        
                        # Display enhanced scoring breakdown
                        if 'semantic_score' in analysis_result:
                            st.markdown("**Enhanced Analysis:**")
                            st.write(f"🎯 Keyword Match: {analysis_result['keyword_score']}%")
                            st.write(f"🧠 Semantic Similarity: {analysis_result['semantic_score']}%")
                            
                            # Show semantic insights
                            semantic_data = analysis_result.get('semantic_analysis', {})
                            if semantic_data.get('strong_matches'):
                                st.write(f"✨ Strong Conceptual Matches: {len(semantic_data['strong_matches'])}")
                            if semantic_data.get('conceptual_gaps'):
                                st.write(f"⚠️ Conceptual Gaps: {len(semantic_data['conceptual_gaps'])}")
                        
                        # Score interpretation
                        if overall_score >= 70:
                            st.success("Excellent match! Your resume aligns well with the job requirements.")
                        elif overall_score >= 40:
                            st.warning("Good match with room for improvement.")
                        else:
                            st.error("Low match score. Consider tailoring your resume more closely to the job description.")
                    
                    with result_col2:
                        st.subheader("Personalized Improvement Suggestions")
                        
                        # Display generated suggestions with improved formatting
                        for i, suggestion in enumerate(suggestions, 1):
                            suggestion_type = suggestion.get('type', 'general')
                            suggestion_text = suggestion.get('text', '')
                            
                            # Style suggestions based on type
                            if suggestion_type == 'success':
                                st.success(f"🎉 {suggestion_text}")
                            elif suggestion_type == 'technical':
                                st.info(f"🔧 {suggestion_text}")
                            elif suggestion_type == 'soft_skill':
                                st.info(f"💼 {suggestion_text}")
                            elif suggestion_type == 'keyword':
                                st.info(f"📝 {suggestion_text}")
                            elif suggestion_type == 'strategy':
                                st.warning(f"💡 {suggestion_text}")
                            else:
                                st.write(f"**{i}.** {suggestion_text}")
                        
                        # Add motivational closing message
                        if overall_score < 70:
                            st.markdown("---")
                            st.markdown("💪 **Remember**: Small, targeted changes to your resume can significantly improve your match score. Focus on the most relevant skills for this specific role!")
                        
                        # Quick action items section
                        if analysis_result['missing']['technical'] or analysis_result['missing']['soft_skills']:
                            st.markdown("---")
                            st.markdown("**Quick Action Items:**")
                            
                            action_items = []
                            if analysis_result['missing']['technical']:
                                top_tech = list(analysis_result['missing']['technical'])[:3]
                                action_items.append(f"• Review your Skills section - consider adding: {', '.join(top_tech)}")
                            
                            if analysis_result['missing']['soft_skills']:
                                top_soft = list(analysis_result['missing']['soft_skills'])[:2]
                                action_items.append(f"• Enhance your Experience descriptions to highlight: {', '.join(top_soft)}")
                            
                            if len(analysis_result['matches']['all']) > 0:
                                action_items.append("• Great job on the keywords you already have - keep those prominent!")
                            
                            for item in action_items:
                                st.markdown(item)
                    
                    # PDF Download Section
                    st.markdown("---")
                    col_download1, col_download2 = st.columns([2, 1])
                    
                    with col_download1:
                        st.markdown("**📄 Download Your Analysis Report**")
                        st.write("Get a comprehensive PDF report with your match score, missing skills, and personalized suggestions.")
                    
                    with col_download2:
                        # Generate PDF report
                        pdf_generator = ResumeAnalysisReportGenerator()
                        
                        # Prepare filename and job title for the report
                        resume_filename = resume_file.name if resume_file else "Resume"
                        job_title = "Job Position"  # Could be enhanced to extract from job description
                        
                        # Generate PDF
                        pdf_bytes = pdf_generator.generate_report(
                            analysis_result=analysis_result,
                            suggestions=suggestions,
                            resume_filename=resume_filename,
                            job_title=job_title
                        )
                        
                        # Create download button
                        download_filename = f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_bytes,
                            file_name=download_filename,
                            mime="application/pdf",
                            type="primary",
                            help="Download a detailed PDF report with your analysis results"
                        )
                    
                    # Display semantic analysis details
                    if 'semantic_analysis' in analysis_result and analysis_result['semantic_analysis'].get('semantic_matches'):
                        with st.expander("🧠 Semantic Analysis Details", expanded=False):
                            semantic_data = analysis_result['semantic_analysis']
                            
                            if semantic_data.get('strong_matches'):
                                st.subheader("💪 Strong Conceptual Matches")
                                for match in semantic_data['strong_matches'][:5]:
                                    st.write(f"**Job Requirement:** {match['job_sentence'][:100]}...")
                                    st.write(f"**Your Experience:** {match['resume_sentence'][:100]}...")
                                    st.write(f"**Similarity:** {match['similarity']:.2f}")
                                    st.markdown("---")
                            
                            if semantic_data.get('conceptual_gaps'):
                                st.subheader("🎯 Areas for Improvement")
                                for gap in semantic_data['conceptual_gaps'][:3]:
                                    st.write(f"• {gap}")
                    
                    # Display matched keywords in an expander
                    with st.expander("🔍 View Matched Keywords", expanded=False):
                        col_matched, col_missing = st.columns(2)
                        
                        with col_matched:
                            st.subheader("✅ Keywords Found")
                            if analysis_result['matches']['technical']:
                                st.write("**Technical:**")
                                st.write(", ".join(list(analysis_result['matches']['technical'])[:10]))
                            if analysis_result['matches']['soft_skills']:
                                st.write("**Soft Skills:**")
                                st.write(", ".join(list(analysis_result['matches']['soft_skills'])[:8]))
                        
                        with col_missing:
                            st.subheader("❌ Keywords Missing")
                            if analysis_result['missing']['technical']:
                                st.write("**Technical:**")
                                st.write(", ".join(list(analysis_result['missing']['technical'])[:10]))
                            if analysis_result['missing']['soft_skills']:
                                st.write("**Soft Skills:**")
                                st.write(", ".join(list(analysis_result['missing']['soft_skills'])[:8]))
                    
                    # Display extracted text for verification (in expander)
                    with st.expander("📄 View Extracted Text (for verification)", expanded=False):
                        col_resume, col_job = st.columns(2)
                        
                        with col_resume:
                            st.subheader("Resume Text")
                            st.text_area("Extracted Resume Content", resume_text[:500] + "..." if len(resume_text) > 500 else resume_text, height=200, disabled=True)
                        
                        with col_job:
                            st.subheader("Job Description Text")
                            st.text_area("Extracted Job Description Content", job_desc_text[:500] + "..." if len(job_desc_text) > 500 else job_desc_text, height=200, disabled=True)
                
                except Exception as e:
                    st.error(f"An error occurred while processing the files: {str(e)}")
                    st.error("Please check that your files are valid PDF or DOCX documents and try again.")

if __name__ == "__main__":
    main()
