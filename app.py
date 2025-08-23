import streamlit as st
import os
from datetime import datetime
import io
import time

# Simple imports without complex dependencies first
try:
    from utils.file_processor import extract_text_from_file, validate_file_type
    from utils.nlp_analyzer import ResumeJobMatcher
    from utils.pdf_generator import ResumeAnalysisReportGenerator
    FULL_FEATURES = True
except ImportError as e:
    st.error(f"Import error: {e}")
    FULL_FEATURES = False

# Custom CSS for minimalist, modern styling
def add_custom_css():
    st.markdown("""
    <style>
    /* Base styles */
    :root {
        --accent-color: #0ea5e9; /* Sky blue accent */
        --accent-hover: #0284c7;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --bg-primary: #ffffff;
        --bg-secondary: #f8fafc;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
    }

    /* Global styles */
    body {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }

    /* Main container */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }

    /* Header */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 1rem;
    }

    .header-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        letter-spacing: -0.025em;
    }

    .header-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .header-accent {
        width: 48px;
        height: 4px;
        background-color: var(--accent-color);
        margin: 1.5rem auto;
        border-radius: 2px;
    }

    /* Section cards */
    .section-card {
        background: var(--bg-primary);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.2s ease;
    }

    .section-card:hover {
        box-shadow: var(--shadow-md);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .section-title-icon {
        color: var(--accent-color);
    }

    /* Input styles */
    .stTextArea textarea, .stFileUploader {
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        background: var(--bg-primary);
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .stTextArea textarea:focus, .stFileUploader:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
        outline: none;
    }

    .stRadio > div {
        display: flex;
        gap: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: background-color 0.15s ease, transform 0.1s ease;
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background-color: var(--accent-hover);
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25);
        outline: none;
    }

    /* Progress bars */
    .progress-container {
        margin: 1.5rem 0;
    }

    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .progress-bar-container {
        height: 10px;
        background-color: var(--border-color);
        border-radius: 5px;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        border-radius: 5px;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .low-score { background-color: var(--error-color); }
    .medium-score { background-color: var(--warning-color); }
    .high-score { background-color: var(--success-color); }

    /* Circular gauge */
    .gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 1.5rem 0;
    }

    .gauge-wrapper {
        position: relative;
        width: 180px;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .gauge-background {
        fill: none;
        stroke: var(--border-color);
        stroke-width: 10;
    }

    .gauge-progress {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 10;
        stroke-linecap: round;
        transform: rotate(-90deg);
        transform-origin: center;
        transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .gauge-text {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .gauge-percentage {
        display: block;
    }

    .gauge-label {
        margin-top: 1rem;
        font-size: 1.125rem;
        font-weight: 500;
        color: var(--text-primary);
    }

    /* Info cards */
    .info-card {
        border-radius: var(--radius-md);
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }

    .info-card-icon {
        font-size: 1.25rem;
        flex-shrink: 0;
    }

    .info-card-content {
        flex: 1;
    }

    .info-card-title {
        font-weight: 600;
        margin-bottom: 0.25rem;
        font-size: 0.875rem;
    }

    .info-card-text {
        font-size: 0.875rem;
        line-height: 1.5;
        color: var(--text-secondary);
    }

    .info-card-success {
        background-color: #f0fdf4;
        border-color: #bbf7d0;
    }

    .info-card-success .info-card-icon {
        color: var(--success-color);
    }

    .info-card-warning {
        background-color: #fffbeb;
        border-color: #fde68a;
    }

    .info-card-warning .info-card-icon {
        color: var(--warning-color);
    }

    .info-card-error {
        background-color: #fef2f2;
        border-color: #fecaca;
    }

    .info-card-error .info-card-icon {
        color: var(--error-color);
    }

    .info-card-suggestion {
        background-color: #f0f9ff;
        border-color: #bae6fd;
    }

    .info-card-suggestion .info-card-icon {
        color: var(--accent-color);
    }

    /* Loading spinner */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem;
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        margin: 1.5rem 0;
    }

    .spinner {
        width: 3rem;
        height: 3rem;
        border: 4px solid rgba(14, 165, 233, 0.2);
        border-top: 4px solid var(--accent-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 500;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 2rem;
        color: var(--text-secondary);
        font-size: 0.875rem;
        border-top: 1px solid var(--border-color);
    }

    .footer-link {
        color: var(--accent-color);
        text-decoration: none;
        font-weight: 500;
    }

    .footer-link:hover {
        text-decoration: underline;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main {
            padding: 0 0.75rem;
        }

        .header-title {
            font-size: 1.75rem;
        }

        .section-card {
            padding: 1.25rem;
        }

        .gauge-wrapper {
            width: 150px;
            height: 150px;
        }

        .gauge-text {
            font-size: 1.75rem;
        }
    }

    @media (max-width: 480px) {
        .header-title {
            font-size: 1.5rem;
        }

        .section-title {
            font-size: 1.125rem;
        }

        .gauge-wrapper {
            width: 120px;
            height: 120px;
        }

        .gauge-text {
            font-size: 1.5rem;
        }
    }

    /* Divider */
    .section-divider {
        border: 0;
        height: 1px;
        background-color: var(--border-color);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to create a circular gauge with animation
def create_circular_gauge(score, label="Match Score"):
    # Calculate the stroke-dasharray values for the gauge
    radius = 80
    circumference = 2 * 3.14159 * radius
    progress = (score / 100) * circumference
    
    st.markdown(f"""
    <div class="gauge-container">
        <div class="gauge-wrapper">
            <svg width="180" height="180" viewBox="0 0 180 180">
                <circle class="gauge-background" cx="90" cy="90" r="{radius}"></circle>
                <circle class="gauge-progress" cx="90" cy="90" r="{radius}" 
                    stroke-dasharray="{circumference}" 
                    stroke-dashoffset="{circumference - progress}"></circle>
            </svg>
            <div class="gauge-text">
                <span class="gauge-percentage">{score:.0f}%</span>
            </div>
        </div>
        <div class="gauge-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

# Function to create a linear progress bar with color coding
def create_progress_bar(score, label="Match Score"):
    # Determine color class based on score
    if score < 60:
        color_class = "low-score"
    elif score < 80:
        color_class = "medium-score"
    else:
        color_class = "high-score"
    
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-label">
            <span>{label}</span>
            <span>{score:.1f}%</span>
        </div>
        <div class="progress-bar-container">
            <div class="progress-bar {color_class}" style="width: {score}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Function to create info cards with icons
def create_info_card(icon, title, content, card_type="suggestion"):
    card_classes = {
        "success": "info-card-success",
        "warning": "info-card-warning",
        "error": "info-card-error",
        "suggestion": "info-card-suggestion"
    }
    
    st.markdown(f"""
    <div class="info-card {card_classes.get(card_type, 'info-card-suggestion')}">
        <div class="info-card-icon">{icon}</div>
        <div class="info-card-content">
            <div class="info-card-title">{title}</div>
            <div class="info-card-text">{content}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="AI Resume Match Checker",
        page_icon="📄",
        layout="wide"
    )
    
    # Add custom CSS
    add_custom_css()
    
    # Minimalist header
    st.markdown("""
    <div class="app-header">
        <h1 class="header-title">AI Resume Match Checker</h1>
        <p class="header-subtitle">Analyze how well your resume matches job descriptions with AI-powered insights</p>
        <div class="header-accent"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # About section in expander
    with st.expander("About this tool", expanded=False):
        st.markdown("""
        This AI-powered tool analyzes how well your resume matches a job description by:
        - Comparing keywords and skills
        - Evaluating technical and soft skills alignment
        - Providing actionable suggestions for improvement
        - Generating a detailed PDF report
        
        **Tips for best results:**
        - Use a clear job description with specific requirements
        - Upload a well-formatted resume (PDF or DOCX)
        """)
    
    if not FULL_FEATURES:
        create_info_card("❌", "Error", "Some features are not available due to import issues. Please check the logs.", "error")
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
        create_info_card("❌", "Error", "Failed to initialize the matching system. Please refresh the page.", "error")
        return
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    # Resume Input Section
    with col1:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">
                <span class="section-title-icon">📄</span>
                <span>Resume Input</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Option to upload file or paste text
        resume_input_method = st.radio(
            "Choose resume input method:",
            ["Upload File", "Paste Text"],
            horizontal=True,
            key="resume_input"
        )
        
        resume_file = None
        resume_text = ""
        
        if resume_input_method == "Upload File":
            resume_file = st.file_uploader(
                "Upload Resume (PDF or DOCX)",
                type=['pdf', 'docx'],
                help="Upload your resume in PDF or DOCX format",
                key="resume_upload"
            )
            
            # Show resume preview
            if resume_file is not None:
                try:
                    if validate_file_type(resume_file, ['pdf', 'docx']):
                        resume_text = extract_text_from_file(resume_file)
                        if resume_text:
                            create_info_card("✅", "Success", "Resume loaded successfully!", "success")
                            with st.expander("Preview Resume Text"):
                                st.text_area("Resume Content", resume_text[:500] + "..." if len(resume_text) > 500 else resume_text, height=150)
                        else:
                            create_info_card("❌", "Error", "Could not extract text from resume. Please check the file.", "error")
                    else:
                        create_info_card("⚠️", "Invalid File", "Please upload PDF or DOCX files only.", "warning")
                except Exception as e:
                    create_info_card("❌", "Error", f"Error processing resume: {e}", "error")
        else:  # Paste Text
            resume_text = st.text_area(
                "Paste Resume Text",
                height=200,
                placeholder="Paste your resume text here...",
                key="resume_paste"
            )
            if resume_text:
                create_info_card("✅", "Success", "Resume text received!", "success")
                with st.expander("Preview Resume Text"):
                    st.text_area("Resume Content", resume_text[:500] + "..." if len(resume_text) > 500 else resume_text, height=150, key="resume_preview")
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Job Description Section
    with col2:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">
                <span class="section-title-icon">📋</span>
                <span>Job Description</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Option to upload file or paste text
        job_input_method = st.radio(
            "Choose job description input method:",
            ["Upload File", "Paste Text"],
            horizontal=True,
            key="job_input"
        )
        
        job_text = ""
        job_file = None
        
        if job_input_method == "Upload File":
            job_file = st.file_uploader(
                "Upload Job Description (PDF or DOCX)",
                type=['pdf', 'docx'],
                help="Upload the job description in PDF or DOCX format",
                key="job_upload"
            )
            
            if job_file is not None:
                try:
                    if validate_file_type(job_file, ['pdf', 'docx']):
                        job_text = extract_text_from_file(job_file)
                        if job_text:
                            create_info_card("✅", "Success", "Job description loaded successfully!", "success")
                            with st.expander("Preview Job Description"):
                                st.text_area("Job Description", job_text[:500] + "..." if len(job_text) > 500 else job_text, height=150, key="job_preview_file")
                        else:
                            create_info_card("❌", "Error", "Could not extract text from job description.", "error")
                    else:
                        create_info_card("⚠️", "Invalid File", "Please upload PDF or DOCX files only.", "warning")
                except Exception as e:
                    create_info_card("❌", "Error", f"Error processing job description: {e}", "error")
        
        else:  # Paste Text
            job_text = st.text_area(
                "Paste Job Description",
                height=200,
                placeholder="Paste the job description here...",
                key="job_paste"
            )
            if job_text:
                create_info_card("✅", "Success", "Job description text received!", "success")
                with st.expander("Preview Job Description"):
                    st.text_area("Job Description", job_text[:500] + "..." if len(job_text) > 500 else job_text, height=150, key="job_preview_text")
        
        st.markdown("</div>", unsafe_allow_html=True)

    # Analysis section
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    # Submit button
    analyze_button = st.button("Analyze Resume Match", type="primary", use_container_width=True)
    
    if analyze_button:
        # Check if we have resume text from either input method
        has_resume = (resume_input_method == "Upload File" and resume_file is not None) or (resume_input_method == "Paste Text" and len(resume_text.strip()) > 0)
        # Check if we have job description text from either input method
        has_job = (job_input_method == "Upload File" and job_file is not None) or (job_input_method == "Paste Text" and len(job_text.strip()) > 0)
        
        if has_resume and has_job:
            try:
                # Get resume text if it wasn't already pasted
                if resume_input_method == "Upload File" and resume_file is not None:
                    resume_text = extract_text_from_file(resume_file)
                
                if not resume_text or not job_text:
                    create_info_card("❌", "Error", "Could not extract text from one or both inputs. Please try again.", "error")
                    return
                
                # Perform analysis with loading experience
                with st.spinner(""):
                    progress_placeholder = st.empty()
                    progress_placeholder.markdown("""
                    <div class="loading-container">
                        <div class="spinner"></div>
                        <div class="loading-text">Analyzing resume match...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Simulate processing time for better UX
                    time.sleep(0.5)
                    analysis_result = matcher.calculate_match_score(resume_text, job_text)
                
                # Clear loading spinner
                progress_placeholder.empty()
                
                # Display results with enhanced UI
                create_info_card("✅", "Analysis Completed", "Your resume analysis is ready!", "success")
                
                # Results Section
                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        <span class="section-title-icon">🎯</span>
                        <span>Match Results</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Overall score with beautiful circular gauge
                overall_score = analysis_result.get('overall_score', analysis_result['keyword_score'])
                create_circular_gauge(overall_score, "Overall Match Score")
                
                # Detailed scores
                st.markdown("#### Detailed Scores")
                col1, col2, col3 = st.columns(3)
                with col1:
                    create_progress_bar(analysis_result['keyword_score'], "Keyword Match")
                with col2:
                    create_progress_bar(analysis_result['technical_score'], "Technical Skills")
                with col3:
                    create_progress_bar(analysis_result['soft_skills_score'], "Soft Skills")
                
                # Semantic analysis if available
                if analysis_result.get('semantic_score', 0) > 0:
                    st.markdown("#### Semantic Analysis")
                    create_progress_bar(analysis_result['semantic_score'], "Semantic Similarity")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Missing Skills Section
                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        <span class="section-title-icon">🔍</span>
                        <span>Missing Skills</span>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Technical Skills")
                    if analysis_result['missing']['technical']:
                        missing_tech_list = list(analysis_result['missing']['technical'])[:10]
                        # Display as bulleted list
                        bullet_list = "\n".join([f"- {skill}" for skill in missing_tech_list])
                        st.markdown(f"**Missing Technical Skills:**\n{bullet_list}")
                    else:
                        create_info_card("✅", "Great Job!", "All technical skills are covered", "success")
                
                with col2:
                    st.markdown("##### Soft Skills")
                    if analysis_result['missing']['soft_skills']:
                        missing_soft_list = list(analysis_result['missing']['soft_skills'])[:10]
                        # Display as bulleted list
                        bullet_list = "\n".join([f"- {skill}" for skill in missing_soft_list])
                        st.markdown(f"**Missing Soft Skills:**\n{bullet_list}")
                    else:
                        create_info_card("✅", "Great Job!", "All soft skills are covered", "success")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Improvement Suggestions Section
                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        <span class="section-title-icon">💡</span>
                        <span>Improvement Suggestions</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Generate enhanced suggestions using the matcher
                suggestions = matcher.generate_suggestions(analysis_result)
                
                # Display suggestions with appropriate icons and colors
                for i, suggestion in enumerate(suggestions[:8], 1):
                    suggestion_type = suggestion.get('type', 'suggestion')
                    suggestion_text = suggestion.get('text', '')
                    
                    icon_map = {
                        'success': '✅',
                        'improvement': '📈',
                        'focus': '🎯',
                        'strategy': '🧠',
                        'technical': '🔧',
                        'soft_skill': '👥',
                        'keyword': '🔑'
                    }
                    
                    card_type_map = {
                        'success': 'success',
                        'improvement': 'suggestion',
                        'focus': 'warning',
                        'strategy': 'suggestion',
                        'technical': 'warning',
                        'soft_skill': 'warning',
                        'keyword': 'warning'
                    }
                    
                    icon = icon_map.get(suggestion_type, '💡')
                    card_type = card_type_map.get(suggestion_type, 'suggestion')
                    
                    create_info_card(icon, f"Suggestion {i}", suggestion_text, card_type)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # PDF Report Generation Section
                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        <span class="section-title-icon">📊</span>
                        <span>Download Report</span>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    report_generator = ResumeAnalysisReportGenerator()
                    pdf_buffer = report_generator.generate_report(
                        analysis_result,
                        suggestions,
                        resume_filename="Pasted Resume" if resume_input_method == "Paste Text" else (resume_file.name if resume_file else None),
                        job_title="Pasted Job Description" if job_input_method == "Paste Text" else (job_file.name if job_file else None)
                    )
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    create_info_card("❌", "Error", f"Could not generate PDF report: {e}", "error")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            except Exception as e:
                create_info_card("❌", "Error", f"Error during analysis: {e}", "error")
                st.write("Please try again or contact support if the issue persists.")
        else:
            create_info_card("⚠️", "Missing Input", "Please provide both a resume and a job description before analyzing.", "warning")
    
    # Minimalist footer
    st.markdown("""
    <div class="app-footer">
        <p>AI Resume Match Checker | Created by Your Name</p>
        <p><a href="https://github.com/yourusername/resume-match-checker" class="footer-link" target="_blank">View on GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()