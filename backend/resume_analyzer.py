import os
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the ResumeAnalyzer with OpenAI API key"""
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file.")

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                # Create PDF reader object
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None

    def analyze_resume(self, resume_text):
        """
        Analyze resume text using OpenAI API
        
        Args:
            resume_text (str): Text content of the resume
            
        Returns:
            dict: Analysis results including skills, experience, and recommendations
        """
        try:
            # Create the prompt for OpenAI
            prompt = f"""Analyze this resume and provide a detailed analysis in JSON format with the following structure:
            {{
                "skills": ["list of technical and soft skills"],
                "experience_summary": "brief summary of work experience",
                "education": ["list of educational qualifications"],
                "strengths": ["list of key strengths"],
                "areas_for_improvement": ["list of areas that could be improved"],
                "career_level": "estimated career level (entry, mid, senior)",
                "recommendations": ["list of specific recommendations for improvement"]
            }}

            Resume text:
            {resume_text}
            """

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume analyzer. Provide detailed and constructive feedback in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Extract and parse the response
            analysis_text = response.choices[0].message.content.strip()
            
            # Clean the response text to ensure it's valid JSON
            # Remove any markdown code block indicators if present
            analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
            
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {str(e)}")
                print("Raw response:", analysis_text)
                return None

        except Exception as e:
            print(f"Error analyzing resume: {str(e)}")
            return None

    def process_resume(self, pdf_path):
        """
        Process a resume PDF file and return analysis
        
        Args:
            pdf_path (str): Path to the resume PDF file
            
        Returns:
            dict: Complete analysis of the resume
        """
        try:
            # Extract text from PDF
            resume_text = self.extract_text_from_pdf(pdf_path)
            if not resume_text:
                return {"error": "Failed to extract text from PDF"}

            # Analyze the resume
            analysis = self.analyze_resume(resume_text)
            if not analysis:
                return {"error": "Failed to analyze resume"}

            return analysis

        except Exception as e:
            print(f"Error processing resume: {str(e)}")
            return {"error": str(e)}

def main():
    """Main function to demonstrate usage"""
    try:
        # Initialize analyzer
        analyzer = ResumeAnalyzer()
        
        # Process resume
        pdf_path = "resume.pdf"  # Update this path to your resume file
        results = analyzer.process_resume(pdf_path)
        
        # Print results
        if "error" in results:
            print(f"Error: {results['error']}")
        else:
            print("\nResume Analysis Results:")
            print("\nSkills:")
            for skill in results["skills"]:
                print(f"- {skill}")
            
            print("\nExperience Summary:")
            print(results["experience_summary"])
            
            print("\nEducation:")
            for edu in results["education"]:
                print(f"- {edu}")
            
            print("\nStrengths:")
            for strength in results["strengths"]:
                print(f"- {strength}")
            
            print("\nAreas for Improvement:")
            for area in results["areas_for_improvement"]:
                print(f"- {area}")
            
            print(f"\nCareer Level: {results['career_level']}")
            
            print("\nRecommendations:")
            for rec in results["recommendations"]:
                print(f"- {rec}")

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main() 