import spacy
import re
from collections import Counter
from typing import List, Dict, Tuple, Set
import string

class ResumeJobMatcher:
    def __init__(self):
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not found
            print("spaCy model not found, using basic text processing")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s-]', ' ', text)
        return text.lower()
    
    def extract_keywords_spacy(self, text: str) -> Set[str]:
        """Extract keywords using spaCy NLP"""
        if not self.nlp:
            return self.extract_keywords_basic(text)
        
        doc = self.nlp(text)
        keywords = set()
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE', 'EVENT']:
                keywords.add(ent.text.lower().strip())
        
        # Extract noun chunks (potential skills/technologies)
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()
            if len(chunk_text) > 2 and len(chunk_text.split()) <= 3:
                keywords.add(chunk_text)
        
        # Extract tokens that look like skills/technologies
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.add(token.lemma_.lower())
        
        return keywords
    
    def extract_keywords_basic(self, text: str) -> Set[str]:
        """Basic keyword extraction without spaCy"""
        # Common technical skills and keywords
        tech_patterns = [
            r'\b(?:python|java|javascript|react|angular|vue|node\.?js|typescript|html|css|sql|mysql|postgresql|mongodb|redis|docker|kubernetes|aws|azure|gcp|git|github|linux|windows|macos)\b',
            r'\b(?:machine learning|data science|artificial intelligence|deep learning|neural networks|tensorflow|pytorch|scikit-learn|pandas|numpy)\b',
            r'\b(?:project management|agile|scrum|kanban|jira|confluence|slack|microsoft office|excel|powerpoint|word)\b',
            r'\b(?:communication|leadership|teamwork|problem solving|analytical|creative|detail oriented|time management)\b'
        ]
        
        keywords = set()
        text_lower = text.lower()
        
        # Extract technical patterns
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            keywords.update(matches)
        
        # Extract potential skills (2-3 word phrases)
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', text_lower)
        
        # Common stop words to exclude
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
        
        # Extract meaningful words
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.add(word)
        
        return keywords
    
    def extract_skills_and_keywords(self, text: str) -> Dict[str, Set[str]]:
        """Extract both technical and soft skills"""
        cleaned_text = self.clean_text(text)
        
        # Use spaCy if available, otherwise use basic extraction
        if self.nlp:
            all_keywords = self.extract_keywords_spacy(cleaned_text)
        else:
            all_keywords = self.extract_keywords_basic(cleaned_text)
        
        # Categorize keywords (basic categorization)
        technical_keywords = set()
        soft_skills = set()
        general_keywords = set()
        
        technical_terms = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs', 'typescript',
            'html', 'css', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github', 'linux', 'windows',
            'machine learning', 'data science', 'ai', 'tensorflow', 'pytorch', 'pandas',
            'numpy', 'scikit-learn', 'excel', 'powerpoint', 'word', 'office'
        }
        
        soft_skill_terms = {
            'communication', 'leadership', 'teamwork', 'management', 'analytical',
            'creative', 'problem solving', 'time management', 'organization',
            'presentation', 'writing', 'research'
        }
        
        for keyword in all_keywords:
            keyword_lower = keyword.lower()
            if any(tech in keyword_lower for tech in technical_terms):
                technical_keywords.add(keyword)
            elif any(soft in keyword_lower for soft in soft_skill_terms):
                soft_skills.add(keyword)
            else:
                general_keywords.add(keyword)
        
        return {
            'technical': technical_keywords,
            'soft_skills': soft_skills,
            'general': general_keywords,
            'all': all_keywords
        }
    
    def calculate_match_score(self, resume_text: str, job_description_text: str) -> Dict:
        """Calculate match score between resume and job description"""
        
        # Extract keywords from both texts
        resume_keywords = self.extract_skills_and_keywords(resume_text)
        job_keywords = self.extract_skills_and_keywords(job_description_text)
        
        # Calculate matches
        technical_matches = resume_keywords['technical'].intersection(job_keywords['technical'])
        soft_skill_matches = resume_keywords['soft_skills'].intersection(job_keywords['soft_skills'])
        general_matches = resume_keywords['general'].intersection(job_keywords['general'])
        
        # Calculate overall matches
        all_job_keywords = job_keywords['all']
        all_resume_keywords = resume_keywords['all']
        all_matches = all_resume_keywords.intersection(all_job_keywords)
        
        # Calculate scores
        total_job_keywords = len(all_job_keywords)
        if total_job_keywords == 0:
            overall_score = 0
        else:
            overall_score = (len(all_matches) / total_job_keywords) * 100
        
        # Calculate category scores
        tech_score = (len(technical_matches) / max(len(job_keywords['technical']), 1)) * 100
        soft_score = (len(soft_skill_matches) / max(len(job_keywords['soft_skills']), 1)) * 100
        
        # Find missing keywords
        missing_technical = job_keywords['technical'] - resume_keywords['technical']
        missing_soft_skills = job_keywords['soft_skills'] - resume_keywords['soft_skills']
        missing_general = job_keywords['general'] - resume_keywords['general']
        
        return {
            'overall_score': round(overall_score, 1),
            'technical_score': round(tech_score, 1),
            'soft_skills_score': round(soft_score, 1),
            'matches': {
                'technical': technical_matches,
                'soft_skills': soft_skill_matches,
                'general': general_matches,
                'all': all_matches
            },
            'missing': {
                'technical': missing_technical,
                'soft_skills': missing_soft_skills,
                'general': missing_general
            },
            'total_job_keywords': total_job_keywords,
            'total_matches': len(all_matches),
            'keywords_found': {
                'resume': resume_keywords,
                'job': job_keywords
            }
        }
    
    def generate_suggestions(self, analysis_result: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        missing = analysis_result['missing']
        scores = {
            'overall': analysis_result['overall_score'],
            'technical': analysis_result['technical_score'],
            'soft_skills': analysis_result['soft_skills_score']
        }
        
        # Overall score suggestions
        if scores['overall'] < 30:
            suggestions.append("Your resume has low keyword overlap with the job description. Consider tailoring your resume more closely to the job requirements.")
        elif scores['overall'] < 60:
            suggestions.append("Your resume shows moderate alignment with the job. Adding more relevant keywords could improve your match score.")
        else:
            suggestions.append("Great job! Your resume shows strong alignment with the job requirements.")
        
        # Technical skills suggestions
        if missing['technical'] and scores['technical'] < 70:
            top_missing_tech = list(missing['technical'])[:5]
            suggestions.append(f"Consider adding these technical skills to your resume: {', '.join(top_missing_tech)}")
        
        # Soft skills suggestions  
        if missing['soft_skills'] and scores['soft_skills'] < 70:
            top_missing_soft = list(missing['soft_skills'])[:3]
            suggestions.append(f"Highlight these soft skills in your resume: {', '.join(top_missing_soft)}")
        
        # General missing keywords
        if missing['general']:
            top_missing_general = list(missing['general'])[:5]
            suggestions.append(f"Important keywords missing from your resume: {', '.join(top_missing_general)}")
        
        # Match suggestions
        total_matches = analysis_result['total_matches']
        if total_matches < 5:
            suggestions.append("Try to incorporate more job-specific terminology and requirements from the job description into your resume.")
        
        return suggestions[:6]  # Limit to 6 suggestions