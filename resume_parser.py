"""
Resume Parser for VEO Video Generation
=======================================
Parses PDF/DOCX resumes and extracts structured data for dialogue generation.
"""

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import PyPDF2
import docx
from groq import Groq


class ResumeParser:
    """
    Parses resume files (PDF/DOCX) and extracts structured information.
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parses resume file and returns structured data.
        """
        
        # Extract text based on file type
        if file_path.lower().endswith('.pdf'):
            raw_text = self._extract_pdf_text(file_path)
        elif file_path.lower().endswith('.docx'):
            raw_text = self._extract_docx_text(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        
        # Use LLM to extract structured data
        structured_data = self._extract_structured_data(raw_text)
        
        structured_data['raw_text'] = raw_text
        structured_data['parsed_at'] = datetime.utcnow().isoformat()
        
        return structured_data
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        
        return text.strip()
    
    def _extract_structured_data(self, text: str) -> Dict[str, Any]:
        """
        Uses LLM to extract structured data from resume text.
        """
        
        prompt = f"""
Extract information from this resume.

RESUME TEXT:
{text}

RETURN ONLY THIS JSON (no markdown):
{{
  "personal_info": {{
    "name": "Full name",
    "email": "email@example.com",
    "phone": "+1234567890",
    "location": "City, State/Country",
    "linkedin": "LinkedIn URL if present",
    "github": "GitHub URL if present"
  }},
  "professional_summary": "2-3 sentence summary",
  "current_role": "Current job title",
  "years_of_experience": "X years",
  "key_strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "skills": {{
    "technical": ["Skill1", "Skill2"],
    "soft": ["Communication", "Leadership"],
    "tools": ["Tool1", "Tool2"]
  }},
  "experience": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration": "Month Year - Month Year",
      "achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "institution": "University Name",
      "degree": "Degree Name",
      "field": "Field of Study",
      "graduation_year": "Year"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech1", "Tech2"]
    }}
  ],
  "certifications": ["Cert 1", "Cert 2"],
  "achievements": ["Achievement 1"],
  "speaking_tone_suggestion": "professional/friendly/confident"
}}

Return ONLY valid JSON. If section not found, use empty array [] or empty string "".
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract info and return ONLY valid JSON. No markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            raw_response = response.choices[0].message.content
            cleaned = self._clean_json_response(raw_response)
            structured_data = json.loads(cleaned)
            structured_data['is_fallback'] = False
            structured_data['warnings'] = []
            
            return structured_data
            
        except Exception as e:
            print(f"⚠️  LLM extraction failed: {e}")
            return self._fallback_extraction(text)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean LLM response."""
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1:
            response = response[start:end+1]
        
        return response.strip()
    
    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback extraction."""
        lines = text.split('\n')
        
        name = "Professional"
        for line in lines:
            if line.strip() and len(line.strip()) > 3:
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line.strip()):
                    name = line.strip()
                    break
        
        email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', text)
        email = email_match.group(0) if email_match else ""
        
        return {
            "personal_info": {
                "name": name,
                "email": email,
                "phone": "",
                "location": ""
            },
            "professional_summary": "Experienced professional.",
            "current_role": "Professional",
            "skills": {"technical": [], "soft": [], "tools": []},
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "speaking_tone_suggestion": "professional",
            "is_fallback": True,
            "warnings": ["AI extraction failed (likely rate limit or connection issue). Using generic fallback data."]
        }
    
    def generate_video_description(self, resume_data: Dict[str, Any], focus: str = "comprehensive") -> str:
        """
        Generates video description from parsed resume data.
        """
        
        personal = resume_data.get('personal_info', {})
        name = personal.get('name', 'Professional')
        summary = resume_data.get('professional_summary', '')
        role = resume_data.get('current_role', 'Professional')
        
        focus_templates = {
            "comprehensive": self._build_comprehensive_description,
            "technical": self._build_technical_description,
            "leadership": self._build_leadership_description,
            "projects": self._build_projects_description
        }
        
        builder = focus_templates.get(focus, self._build_comprehensive_description)
        return builder(resume_data)
    
    def _build_comprehensive_description(self, data: Dict[str, Any]) -> str:
        """Build comprehensive description."""
        personal = data.get('personal_info', {})
        name = personal.get('name', 'Professional')
        role = data.get('current_role', 'Professional')
        summary = data.get('professional_summary', '')
        
        skills = data.get('skills', {}).get('technical', [])
        skills_str = ', '.join(skills[:5]) if skills else "various technologies"
        
        description = f"""
I'm {name}, a {role}. {summary}

I specialize in {skills_str}, with extensive hands-on experience in delivering high-quality solutions.

Throughout my career, I've focused on continuous learning and taking on challenges that push boundaries.

I'm looking forward to opportunities where I can contribute my expertise and continue growing.
""".strip()
        
        return description
    
    def _build_technical_description(self, data: Dict[str, Any]) -> str:
        """Build technical description."""
        personal = data.get('personal_info', {})
        name = personal.get('name', 'Professional')
        
        skills = data.get('skills', {})
        tech_skills = skills.get('technical', [])
        
        tech_str = ', '.join(tech_skills[:5]) if tech_skills else "modern technologies"
        
        description = f"""
I'm {name}, a technical professional with deep expertise in {tech_str}.

I have a proven track record of building scalable, efficient solutions using industry best practices.

I'm always exploring new technologies and staying at the forefront of developments.

I'm excited about opportunities to work on challenging technical problems.
""".strip()
        
        return description
    
    def _build_leadership_description(self, data: Dict[str, Any]) -> str:
        """Build leadership description."""
        personal = data.get('personal_info', {})
        name = personal.get('name', 'Professional')
        role = data.get('current_role', 'Leader')
        
        description = f"""
I'm {name}, a {role} with a track record of leading successful teams and projects.

My approach to leadership is built on empowering team members and fostering collaboration.

I've successfully navigated complex challenges and delivered impactful results.

I'm looking for opportunities to bring my leadership experience to organizations that value innovation.
""".strip()
        
        return description
    
    def _build_projects_description(self, data: Dict[str, Any]) -> str:
        """Build projects description."""
        personal = data.get('personal_info', {})
        name = personal.get('name', 'Professional')
        
        projects = data.get('projects', [])
        
        if not projects:
            return self._build_comprehensive_description(data)
        
        description = f"""
I'm {name}, passionate about building innovative solutions through hands-on projects.

My projects showcase my ability to take ideas from concept to completion with attention to detail.

I approach every project with user-centric design and a focus on delivering real value.

I'm excited to bring this project-driven mindset to new opportunities.
""".strip()
        
        return description
