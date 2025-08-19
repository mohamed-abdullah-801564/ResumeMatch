import spacy
import re
from collections import Counter
from typing import List, Dict, Tuple, Set
import string
from .semantic_analyzer import SemanticResumeAnalyzer

class ResumeJobMatcher:
    def __init__(self):
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not found
            print("spaCy model not found, using basic text processing")
            self.nlp = None
        
        # Initialize semantic analyzer
        self.semantic_analyzer = SemanticResumeAnalyzer()
    
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
        """Calculate enhanced match score including semantic analysis"""
        
        # Extract keywords from both texts
        resume_keywords = self.extract_skills_and_keywords(resume_text)
        job_keywords = self.extract_skills_and_keywords(job_description_text)
        
        # Calculate keyword matches
        technical_matches = resume_keywords['technical'].intersection(job_keywords['technical'])
        soft_skill_matches = resume_keywords['soft_skills'].intersection(job_keywords['soft_skills'])
        general_matches = resume_keywords['general'].intersection(job_keywords['general'])
        
        # Calculate overall keyword matches
        all_job_keywords = job_keywords['all']
        all_resume_keywords = resume_keywords['all']
        all_matches = all_resume_keywords.intersection(all_job_keywords)
        
        # Calculate keyword scores
        total_job_keywords = len(all_job_keywords)
        if total_job_keywords == 0:
            keyword_score = 0
        else:
            keyword_score = (len(all_matches) / total_job_keywords) * 100
        
        # Calculate category scores
        tech_score = (len(technical_matches) / max(len(job_keywords['technical']), 1)) * 100
        soft_score = (len(soft_skill_matches) / max(len(job_keywords['soft_skills']), 1)) * 100
        
        # Perform semantic analysis
        semantic_analysis = self.semantic_analyzer.calculate_semantic_similarity(resume_text, job_description_text)
        
        # Calculate enhanced scores
        enhanced_scores = self.semantic_analyzer.calculate_enhanced_match_score(
            {'overall_score': keyword_score, 'technical_score': tech_score, 'soft_skills_score': soft_score},
            semantic_analysis
        )
        
        # Find missing keywords
        missing_technical = job_keywords['technical'] - resume_keywords['technical']
        missing_soft_skills = job_keywords['soft_skills'] - resume_keywords['soft_skills']
        missing_general = job_keywords['general'] - resume_keywords['general']
        
        return {
            'overall_score': enhanced_scores['enhanced_overall_score'],
            'keyword_score': round(keyword_score, 1),
            'semantic_score': round(semantic_analysis['overall_semantic_similarity'], 1),
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
            'semantic_analysis': semantic_analysis,
            'enhanced_scoring': enhanced_scores,
            'keywords_found': {
                'resume': resume_keywords,
                'job': job_keywords
            }
        }
    
    def generate_suggestions(self, analysis_result: Dict) -> List[Dict[str, str]]:
        """Generate enhanced suggestions based on keyword and semantic analysis"""
        suggestions = []
        
        missing = analysis_result['missing']
        scores = {
            'overall': analysis_result['overall_score'],
            'keyword': analysis_result.get('keyword_score', analysis_result['overall_score']),
            'semantic': analysis_result.get('semantic_score', 0),
            'technical': analysis_result['technical_score'],
            'soft_skills': analysis_result['soft_skills_score']
        }
        
        # Enhanced overall score feedback considering both keyword and semantic analysis
        if scores['overall'] >= 70:
            if scores['semantic'] >= 60:
                suggestions.append({
                    'type': 'success',
                    'text': "Outstanding! Your resume demonstrates both strong keyword alignment and conceptual understanding of the role requirements."
                })
            else:
                suggestions.append({
                    'type': 'success',
                    'text': "Excellent keyword alignment! Consider adding more detailed descriptions to demonstrate deeper understanding of the concepts."
                })
        elif scores['overall'] >= 40:
            suggestions.append({
                'type': 'improvement',
                'text': f"Good foundation with {scores['keyword']:.1f}% keyword match and {scores['semantic']:.1f}% conceptual alignment. Targeted improvements can significantly boost your score."
            })
        else:
            suggestions.append({
                'type': 'focus',
                'text': "Significant opportunity for improvement in both keyword relevance and conceptual alignment with the job requirements."
            })
        
        # Generate semantic suggestions if available
        if 'semantic_analysis' in analysis_result:
            semantic_suggestions = self.semantic_analyzer.generate_semantic_suggestions(
                analysis_result['semantic_analysis'], 
                {'overall_score': scores['keyword']}
            )
            suggestions.extend(semantic_suggestions[:3])
        
        # Detailed technical skills suggestions
        if missing['technical'] and scores['technical'] < 80:
            tech_suggestions = self._generate_technical_suggestions(missing['technical'])
            suggestions.extend(tech_suggestions[:2])  # Limit for space
        
        # Detailed soft skills suggestions  
        if missing['soft_skills'] and scores['soft_skills'] < 80:
            soft_suggestions = self._generate_soft_skill_suggestions(missing['soft_skills'])
            suggestions.extend(soft_suggestions[:2])  # Limit for space
        
        # Strategic advice based on semantic vs keyword balance
        if scores['keyword'] > scores['semantic'] + 20:
            suggestions.append({
                'type': 'strategy',
                'text': "Strong keyword coverage! Focus on providing more detailed examples and context to demonstrate deeper understanding of these skills."
            })
        elif scores['semantic'] > scores['keyword'] + 20:
            suggestions.append({
                'type': 'strategy',
                'text': "Good conceptual alignment! Incorporate more specific keywords and terminology from the job description to improve ATS compatibility."
            })
        
        return suggestions[:8]  # Limit to 8 suggestions
    
    def _generate_technical_suggestions(self, missing_technical: Set[str]) -> List[Dict[str, str]]:
        """Generate specific suggestions for missing technical skills"""
        suggestions = []
        tech_list = list(missing_technical)[:5]
        
        # Mapping of skills to resume section suggestions
        skill_suggestions = {
            'python': "Add Python to your Skills section or mention Python projects in your Experience section (e.g., 'Developed automated scripts using Python')",
            'java': "Include Java in your technical skills or describe Java-based projects in your Experience section",
            'javascript': "Highlight JavaScript experience in your Skills section or mention web development projects using JavaScript",
            'react': "Add React to your frontend skills or describe React applications you've built",
            'sql': "Include SQL in your technical skills or mention database work in your Experience section (e.g., 'Queried databases using SQL')",
            'aws': "Add AWS to your cloud skills or mention cloud infrastructure work in your Experience section",
            'docker': "Include Docker in your DevOps skills or describe containerization experience",
            'git': "Add Git to your version control skills or mention collaborative development experience",
            'machine learning': "Include Machine Learning in your Skills section or describe ML projects in your Experience section",
            'project management': "Highlight project management experience in your Experience section or add PM tools to your Skills section"
        }
        
        for skill in tech_list:
            skill_lower = skill.lower()
            if skill_lower in skill_suggestions:
                suggestions.append({
                    'type': 'technical',
                    'text': f"**{skill.title()}**: {skill_suggestions[skill_lower]}"
                })
            else:
                suggestions.append({
                    'type': 'technical', 
                    'text': f"**{skill.title()}**: Consider adding this skill to your Skills section or describing related experience in your work history"
                })
        
        return suggestions
    
    def _generate_soft_skill_suggestions(self, missing_soft_skills: Set[str]) -> List[Dict[str, str]]:
        """Generate specific suggestions for missing soft skills"""
        suggestions = []
        soft_list = list(missing_soft_skills)[:3]
        
        soft_skill_suggestions = {
            'leadership': "Demonstrate leadership by describing times you led teams, mentored colleagues, or took initiative on projects",
            'communication': "Highlight communication skills by mentioning presentations, client interactions, or cross-team collaboration",
            'teamwork': "Showcase teamwork through examples of collaborative projects or cross-functional work",
            'problem solving': "Illustrate problem-solving abilities by describing challenges you've overcome or innovative solutions you've implemented",
            'management': "Show management experience through examples of supervising others, managing projects, or overseeing processes",
            'analytical': "Demonstrate analytical skills by mentioning data analysis, research projects, or systematic problem-solving approaches"
        }
        
        for skill in soft_list:
            skill_lower = skill.lower()
            if skill_lower in soft_skill_suggestions:
                suggestions.append({
                    'type': 'soft_skill',
                    'text': f"**{skill.title()}**: {soft_skill_suggestions[skill_lower]}"
                })
            else:
                suggestions.append({
                    'type': 'soft_skill',
                    'text': f"**{skill.title()}**: Consider adding examples that demonstrate this skill in your Experience or Summary section"
                })
        
        return suggestions
    
    def _generate_general_suggestions(self, missing_general: Set[str]) -> List[Dict[str, str]]:
        """Generate suggestions for missing general keywords"""
        suggestions = []
        general_list = list(missing_general)[:4]
        
        for keyword in general_list:
            if len(keyword) > 2:  # Only suggest meaningful keywords
                suggestions.append({
                    'type': 'keyword',
                    'text': f"**{keyword.title()}**: Look for opportunities to naturally incorporate this term in your Experience or Skills sections"
                })
        
        return suggestions