import pdfplumber
import re
from typing import Dict, List

def parse_resume(pdf_path: str) -> Dict:
    """
    Parse a resume PDF and extract structured information.
    
    Args:
        pdf_path (str): Path to the PDF resume file
        
    Returns:
        Dict: Structured profile information including skills, experience, and education
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    
    # Extract skills (common programming languages and technologies)
    skills = extract_skills(text)
    
    # Extract experience
    experience = extract_experience(text)
    
    # Extract education
    education = extract_education(text)
    
    # Create structured profile
    profile = {
        'skills': skills,
        'experience': experience,
        'education': education,
        'raw_text': text
    }
    
    return profile

def extract_skills(text: str) -> List[str]:
    """Extract skills from resume text."""
    # Common programming languages and technologies
    common_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby',
        'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'SQL', 'NoSQL', 'MongoDB',
        'PostgreSQL', 'MySQL', 'React', 'Angular', 'Vue', 'Node.js', 'Django',
        'Flask', 'Spring', 'Express', 'AWS', 'Azure', 'GCP', 'Docker',
        'Kubernetes', 'CI/CD', 'Git', 'Agile', 'Scrum', 'DevOps'
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

def extract_experience(text: str) -> List[Dict]:
    """Extract work experience from resume text."""
    # This is a simple implementation. In a real application, you might want to use
    # more sophisticated NLP techniques or AI models.
    experience = []
    
    # Look for common job title patterns
    job_patterns = [
        r'(?i)(senior|lead|principal)?\s*(software|full stack|frontend|backend|devops|data|qa|test|automation)\s*(engineer|developer|architect|specialist)',
        r'(?i)(software|full stack|frontend|backend|devops|data|qa|test|automation)\s*(engineer|developer|architect|specialist)',
    ]
    
    for pattern in job_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get some context around the match
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            experience.append({
                'title': match.group(0),
                'context': context.strip()
            })
    
    return experience

def extract_education(text: str) -> List[Dict]:
    """Extract education information from resume text."""
    education = []
    
    # Look for common degree patterns
    degree_patterns = [
        r'(?i)(bachelor|master|phd|b\.s\.|m\.s\.|b\.a\.|m\.a\.)\s*(of|in)?\s*(science|arts|engineering|computer science|information technology)',
        r'(?i)(b\.s\.|m\.s\.|b\.a\.|m\.a\.|ph\.d\.)',
    ]
    
    for pattern in degree_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get some context around the match
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]
            
            education.append({
                'degree': match.group(0),
                'context': context.strip()
            })
    
    return education 