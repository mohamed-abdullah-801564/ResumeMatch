import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Set
import re
import spacy
from collections import defaultdict

class SemanticResumeAnalyzer:
    def __init__(self):
        # Use TF-IDF for semantic similarity analysis
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=5000,
            lowercase=True
        )
        
        # Load spaCy model for text processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found, using basic text processing")
            self.nlp = None
        
        # Skill synonym mapping for enhanced matching
        self.skill_synonyms = {
            'python': ['python programming', 'python development', 'python scripting'],
            'javascript': ['js', 'javascript programming', 'frontend development'],
            'machine learning': ['ml', 'artificial intelligence', 'ai', 'data science'],
            'project management': ['pm', 'project coordination', 'project leadership'],
            'communication': ['verbal communication', 'written communication', 'interpersonal skills'],
            'leadership': ['team leadership', 'team management', 'leading teams'],
            'sql': ['database', 'database management', 'data querying'],
            'react': ['reactjs', 'react.js', 'frontend framework'],
            'aws': ['amazon web services', 'cloud computing', 'cloud services']
        }
    
    def extract_sentences_and_phrases(self, text: str) -> List[str]:
        """Extract meaningful sentences and phrases from text"""
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
            
            # Also extract noun phrases that might represent skills/concepts
            noun_phrases = [chunk.text.strip() for chunk in doc.noun_chunks 
                          if len(chunk.text.strip()) > 3 and len(chunk.text.split()) <= 4]
            
            return sentences + noun_phrases
        else:
            # Fallback: simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def calculate_semantic_similarity(self, resume_text: str, job_description_text: str) -> Dict:
        """Calculate semantic similarity using TF-IDF and enhanced matching"""
        try:
            # Extract sentences and phrases
            resume_sentences = self.extract_sentences_and_phrases(resume_text)
            job_sentences = self.extract_sentences_and_phrases(job_description_text)
            
            if not resume_sentences or not job_sentences:
                return self._fallback_similarity_analysis(resume_text, job_description_text)
            
            # Enhance text with synonyms
            enhanced_resume = self._enhance_with_synonyms(resume_text)
            enhanced_job = self._enhance_with_synonyms(job_description_text)
            
            # Create TF-IDF vectors
            all_texts = [enhanced_resume, enhanced_job] + resume_sentences + job_sentences
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity between enhanced texts
            overall_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Calculate sentence-level similarities
            resume_vectors = tfidf_matrix[2:2+len(resume_sentences)]
            job_vectors = tfidf_matrix[2+len(resume_sentences):]
            
            similarity_matrix = cosine_similarity(resume_vectors, job_vectors)
            
            # Find best matches for each job requirement
            best_matches = []
            semantic_matches = []
            
            for i, job_sentence in enumerate(job_sentences):
                if i < similarity_matrix.shape[1]:
                    max_similarity = np.max(similarity_matrix[:, i])
                    best_resume_idx = np.argmax(similarity_matrix[:, i])
                    
                    if max_similarity > 0.3:  # Lower threshold for TF-IDF
                        semantic_matches.append({
                            'job_sentence': job_sentence,
                            'resume_sentence': resume_sentences[best_resume_idx],
                            'similarity': float(max_similarity)
                        })
                    
                    best_matches.append({
                        'job_sentence': job_sentence,
                        'best_resume_match': resume_sentences[best_resume_idx] if best_resume_idx < len(resume_sentences) else "No match",
                        'similarity': float(max_similarity)
                    })
            
            # Identify missing concepts
            missing_concepts = [
                match['job_sentence'] for match in best_matches 
                if match['similarity'] < 0.2
            ]
            
            # Identify strong matches
            strong_matches = [
                match for match in semantic_matches 
                if match['similarity'] > 0.5
            ]
            
            return {
                'overall_semantic_similarity': overall_similarity * 100,
                'semantic_matches': semantic_matches,
                'missing_concepts': missing_concepts[:10],
                'strong_matches': strong_matches,
                'similarity_distribution': self._analyze_similarity_distribution(similarity_matrix),
                'conceptual_gaps': self._identify_conceptual_gaps(missing_concepts)
            }
            
        except Exception as e:
            print(f"Error in semantic analysis: {e}")
            return self._fallback_similarity_analysis(resume_text, job_description_text)
    
    def _fallback_similarity_analysis(self, resume_text: str, job_description_text: str) -> Dict:
        """Fallback analysis when transformer model is not available"""
        # Simple word overlap analysis
        resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
        job_words = set(re.findall(r'\b\w+\b', job_description_text.lower()))
        
        common_words = resume_words.intersection(job_words)
        similarity = len(common_words) / len(job_words) if job_words else 0
        
        return {
            'overall_semantic_similarity': similarity * 100,
            'semantic_matches': [],
            'missing_concepts': [],
            'strong_matches': [],
            'similarity_distribution': {'low': 70, 'medium': 20, 'high': 10},
            'conceptual_gaps': ['Transformer model not available - using basic analysis']
        }
    
    def _analyze_similarity_distribution(self, similarity_matrix: np.ndarray) -> Dict[str, float]:
        """Analyze the distribution of similarity scores"""
        similarities = similarity_matrix.flatten()
        
        high_sim = np.sum(similarities > 0.7) / len(similarities) * 100
        medium_sim = np.sum((similarities > 0.4) & (similarities <= 0.7)) / len(similarities) * 100
        low_sim = np.sum(similarities <= 0.4) / len(similarities) * 100
        
        return {
            'high': float(high_sim),
            'medium': float(medium_sim),
            'low': float(low_sim)
        }
    
    def _identify_conceptual_gaps(self, missing_concepts: List[str]) -> List[str]:
        """Identify key conceptual areas that are missing"""
        gaps = []
        
        # Common skill categories
        tech_keywords = ['programming', 'software', 'development', 'technical', 'coding', 'system']
        management_keywords = ['manage', 'lead', 'project', 'team', 'coordinate']
        communication_keywords = ['communication', 'presentation', 'writing', 'collaboration']
        
        missing_text = ' '.join(missing_concepts).lower()
        
        if any(keyword in missing_text for keyword in tech_keywords):
            gaps.append("Technical skills and programming experience")
        
        if any(keyword in missing_text for keyword in management_keywords):
            gaps.append("Leadership and project management experience")
        
        if any(keyword in missing_text for keyword in communication_keywords):
            gaps.append("Communication and collaboration skills")
        
        return gaps
    
    def _enhance_with_synonyms(self, text: str) -> str:
        """Enhance text by adding synonyms for better semantic matching"""
        enhanced_text = text.lower()
        
        for main_skill, synonyms in self.skill_synonyms.items():
            if main_skill in enhanced_text:
                # Add synonyms to the text for better matching
                enhanced_text += " " + " ".join(synonyms)
        
        return enhanced_text
    
    def generate_semantic_suggestions(self, semantic_analysis: Dict, keyword_analysis: Dict) -> List[Dict[str, str]]:
        """Generate enhanced suggestions based on semantic analysis"""
        suggestions = []
        
        semantic_score = semantic_analysis['overall_semantic_similarity']
        keyword_score = keyword_analysis['overall_score']
        
        # Overall assessment
        if semantic_score >= 70 and keyword_score >= 70:
            suggestions.append({
                'type': 'success',
                'text': "Excellent alignment! Your resume demonstrates both keyword relevance and conceptual understanding of the role requirements."
            })
        elif semantic_score >= 60:
            suggestions.append({
                'type': 'improvement',
                'text': "Your resume shows good conceptual alignment with the role. Focus on incorporating more specific keywords to improve visibility in applicant tracking systems."
            })
        elif keyword_score >= 60:
            suggestions.append({
                'type': 'improvement', 
                'text': "Good keyword coverage! Consider adding more detailed descriptions that demonstrate deeper understanding of the concepts behind these keywords."
            })
        else:
            suggestions.append({
                'type': 'focus',
                'text': "Significant improvements needed. Your resume needs both better keyword alignment and stronger demonstration of relevant concepts and experience."
            })
        
        # Semantic-specific suggestions
        if semantic_analysis['missing_concepts']:
            top_missing = semantic_analysis['missing_concepts'][:3]
            for concept in top_missing:
                if len(concept) > 20:  # Only suggest meaningful concepts
                    suggestions.append({
                        'type': 'semantic',
                        'text': f"**Missing Concept**: Consider adding experience or examples related to: '{concept[:100]}...'"
                    })
        
        # Conceptual gap suggestions
        for gap in semantic_analysis['conceptual_gaps'][:2]:
            suggestions.append({
                'type': 'conceptual',
                'text': f"**Conceptual Gap**: Strengthen your resume by highlighting experience in {gap.lower()}"
            })
        
        # Strong match reinforcement
        if semantic_analysis['strong_matches']:
            suggestions.append({
                'type': 'strength',
                'text': f"Great! You have {len(semantic_analysis['strong_matches'])} strong conceptual matches. Make sure these experiences are prominently featured in your resume."
            })
        
        return suggestions[:6]
    
    def calculate_enhanced_match_score(self, keyword_analysis: Dict, semantic_analysis: Dict) -> Dict:
        """Calculate enhanced match score combining keyword and semantic analysis"""
        keyword_score = keyword_analysis['overall_score']
        semantic_score = semantic_analysis['overall_semantic_similarity']
        
        # Weighted combination: 60% keywords (for ATS), 40% semantic
        enhanced_score = (keyword_score * 0.6) + (semantic_score * 0.4)
        
        # Bonus for strong semantic matches
        if semantic_analysis['strong_matches']:
            bonus = min(len(semantic_analysis['strong_matches']) * 2, 10)
            enhanced_score = min(enhanced_score + bonus, 100)
        
        return {
            'enhanced_overall_score': round(enhanced_score, 1),
            'keyword_component': round(keyword_score, 1),
            'semantic_component': round(semantic_score, 1),
            'keyword_weight': 60,
            'semantic_weight': 40,
            'semantic_bonus': len(semantic_analysis.get('strong_matches', [])) * 2
        }