from flask import Flask, render_template, request, jsonify
import requests
import uuid
import json
import re
import os
from groq import Groq
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)

# Configure Groq client
client = Groq(
    api_key=os.environ.get('GROQ_API_KEY')
)

@app.route('/')
def index():
    return render_template('index.html')

def get_random_theme():
    color_schemes = [
        {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "accent": "#e74c3c",
            "bg": "#f8f9fa",
            "gradient": "135deg, #2c3e50, #3498db"
        },
        {
            "primary": "#1a472a",
            "secondary": "#2ecc71",
            "accent": "#f39c12",
            "bg": "#f5f6fa",
            "gradient": "135deg, #1a472a, #2ecc71"
        },
        {
            "primary": "#2c0735",
            "secondary": "#7d3c98",
            "accent": "#ff5733",
            "bg": "#f7f9fc",
            "gradient": "135deg, #2c0735, #7d3c98"
        },
        {
            "primary": "#34495e",
            "secondary": "#16a085",
            "accent": "#e67e22",
            "bg": "#ecf0f1",
            "gradient": "135deg, #34495e, #16a085"
        },
        {
            "primary": "#273c75",
            "secondary": "#00a8ff",
            "accent": "#fbc531",
            "bg": "#f5f6fa",
            "gradient": "135deg, #273c75, #00a8ff"
        }
    ]
    
    fonts = [
        "'Calibri', Arial, sans-serif",
        "'Helvetica Neue', Arial, sans-serif",
        "'Segoe UI', Arial, sans-serif",
        "'Roboto', Arial, sans-serif",
        "'Open Sans', Arial, sans-serif"
    ]
    
    layouts = [
        {"header_radius": "8px", "card_radius": "8px", "shadow": "0 0 20px rgba(0,0,0,0.1)"},
        {"header_radius": "0", "card_radius": "12px", "shadow": "0 3px 15px rgba(0,0,0,0.08)"},
        {"header_radius": "16px", "card_radius": "6px", "shadow": "0 5px 25px rgba(0,0,0,0.12)"},
        {"header_radius": "4px", "card_radius": "10px", "shadow": "0 2px 12px rgba(0,0,0,0.15)"},
        {"header_radius": "12px", "card_radius": "4px", "shadow": "0 4px 18px rgba(0,0,0,0.1)"}
    ]
    
    return {
        "colors": random.choice(color_schemes),
        "font": random.choice(fonts),
        "layout": random.choice(layouts)
    }

@app.route('/generate_resume', methods=['POST'])
def generate_resume():
    # Get form data
    data = request.get_json()
    
    # Construct resume sections with comprehensive formatting
    resume_sections = []
    
    if data.get('personal_info'):
        resume_sections.append("CONTACT INFORMATION")
        resume_sections.append(f"{data['personal_info'].get('name', '')}")
        resume_sections.append(f"{data['personal_info'].get('address', '')}")
        resume_sections.append(f"Email: {data['personal_info'].get('email', '')}")
        resume_sections.append(f"Phone: {data['personal_info'].get('phone', '')}")
        resume_sections.append(f"LinkedIn: {data['personal_info'].get('linkedin', '')}")
    
    if data.get('summary'):
        resume_sections.append("\nPROFESSIONAL SUMMARY")
        resume_sections.append(data['summary'])
    
    if data.get('experience'):
        resume_sections.append("\nPROFESSIONAL EXPERIENCE")
        resume_sections.append(data['experience'])
    
    if data.get('education'):
        resume_sections.append("\nEDUCATION")
        resume_sections.append(data['education'])
    
    if data.get('skills'):
        resume_sections.append("\nSKILLS")
        resume_sections.append(data['skills'])
    
    if data.get('certifications'):
        resume_sections.append("\nCERTIFICATIONS")
        resume_sections.append(data['certifications'])
    
    if data.get('awards'):
        resume_sections.append("\nAWARDS & ACHIEVEMENTS")
        resume_sections.append(data['awards'])
    
    if data.get('projects'):
        resume_sections.append("\nRELEVANT PROJECTS")
        resume_sections.append(data['projects'])
    
    if data.get('languages'):
        resume_sections.append("\nLANGUAGES")
        resume_sections.append(data['languages'])
    
    if data.get('volunteer'):
        resume_sections.append("\nVOLUNTEER EXPERIENCE")
        resume_sections.append(data['volunteer'])

    # Updated prompt with comprehensive structure
    template = """Create a professional HTML resume with the following structure:

<div class="resume-header">
    <h1>[Full Name]</h1>
    <div class="contact-details">
        [Address]<br>
        Email: [Email] | Phone: [Phone]<br>
        [LinkedIn if provided]
    </div>
</div>

<div class="resume-section">
    <h2>PROFESSIONAL SUMMARY</h2>
    <p class="summary">[Professional summary with key achievements and goals]</p>
</div>

<div class="resume-section">
    <h2>PROFESSIONAL EXPERIENCE</h2>
    <div class="experience-item">
        [For each position:]
        <div class="title">[Job Title] - [Company Name]</div>
        <div class="date">[Start Date] - [End Date] | [Location]</div>
        <ul>
            [Key responsibilities and achievements as list items]
        </ul>
    </div>
</div>

<div class="resume-section">
    <h2>EDUCATION</h2>
    <div class="education-item">
        [Degree/Program]<br>
        [Institution Name] - [Graduation Year]<br>
        [Honors/GPA if applicable]
    </div>
</div>

<div class="resume-section">
    <h2>TECHNICAL SKILLS</h2>
    <ul class="skills-list">
        [Skills categorized and listed]
    </ul>
</div>

[Optional Sections based on provided data:]
- Certifications
- Awards & Achievements
- Projects
- Languages
- Volunteer Experience

Use the following information to fill in the template:

"""

    requirements = """

Requirements:
1. Create a modern, professional layout
2. Use consistent formatting throughout
3. Highlight key achievements and metrics
4. Use bullet points for better readability
5. Include all provided sections, properly formatted
6. Maintain professional spacing and hierarchy
7. Make contact information easily scannable
8. Format dates and company names consistently"""

    prompt = template + '\n'.join(resume_sections) + requirements

    try:
        # Make request to Groq API
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert ATS-optimized resume writer. Follow these key principles:
1. Use industry-standard section headings that ATS systems recognize
2. Include relevant keywords from the user's field naturally
3. Avoid tables, columns, graphics, or complex formatting that can confuse ATS
4. Use standard bullet points (•) instead of fancy symbols
5. Quantify achievements with metrics where possible
6. Use active voice and power verbs
7. Maintain clean HTML structure with semantic tags
8. Focus on achievements rather than just responsibilities"""
                },
                {
                    "role": "user",
                    "content": prompt + """

Additional ATS Requirements:
1. Use proper HTML semantic structure (h1, h2, p, ul, li)
2. Avoid complex CSS styling that might interfere with ATS parsing
3. Use clear section headers: "Experience", "Education", "Skills", etc.
4. Include a skills section with relevant technical and soft skills
5. Use standard date formats (MM/YYYY or YYYY)
6. Incorporate industry-specific keywords naturally
7. Keep formatting simple and consistent
8. Use standard fonts and basic styling
9. Include location information for each position
10. Ensure all acronyms are spelled out at least once"""
                }
            ],
            model="qwen-2.5-32b",
            temperature=0.5,
            max_tokens=4096,
        )
        
        resume_text = completion.choices[0].message.content.strip()
        
        if not resume_text:
            return jsonify({
                'success': False,
                'error': 'Empty response from API'
            })
        
        # Try different patterns to find HTML content
        patterns = [
            r'```html\s*(<!DOCTYPE.*?</html>)\s*```',  # HTML in code block
            r'```\s*(<!DOCTYPE.*?</html>)\s*```',      # HTML in unmarked code block
            r'(<!DOCTYPE.*?</html>)',                  # Raw HTML
            r'<html>.*?</html>',                       # HTML without DOCTYPE
        ]
        
        cleaned_text = None
        for pattern in patterns:
            match = re.search(pattern, resume_text, re.DOTALL | re.IGNORECASE)
            if match:
                cleaned_text = match.group(1)
                break
        
        if not cleaned_text:
            # If no HTML found, try to extract content between tags
            content = re.findall(r'<[^>]+>.*?</[^>]+>', resume_text, re.DOTALL)
            if content:
                theme = get_random_theme()
                style_template = """
                <style>
                    :root {{
                        --primary-color: {theme['colors']['primary']};
                        --secondary-color: {theme['colors']['secondary']};
                        --accent-color: {theme['colors']['accent']};
                        --bg-color: {theme['colors']['bg']};
                        --spacing: 20px;
                    }}

                    body {{
                        font-family: {theme['font']};
                        line-height: 1.6;
                        max-width: 850px;
                        margin: 0 auto;
                        padding: var(--spacing);
                        color: var(--primary-color);
                        background-color: white;
                        box-shadow: {theme['layout']['shadow']};
                    }}

                    .resume-header {{
                        text-align: center;
                        padding: 40px 20px;
                        background: linear-gradient({theme['colors']['gradient']});
                        color: white;
                        border-radius: {theme['layout']['header_radius']};
                        margin-bottom: 30px;
                    }}

                    .resume-header h1 {{
                        font-size: 36px;
                        margin: 0 0 15px 0;
                        letter-spacing: 1px;
                        text-transform: uppercase;
                    }}

                    .contact-details {{
                        font-size: 16px;
                        line-height: 1.8;
                        opacity: 0.9;
                    }}

                    .resume-section {{
                        margin-bottom: 35px;
                        padding: 0 var(--spacing);
                    }}

                    .resume-section h2 {{
                        color: var(--primary-color);
                        font-size: 24px;
                        border-bottom: 3px solid var(--secondary-color);
                        padding-bottom: 8px;
                        margin-bottom: 20px;
                        position: relative;
                    }}

                    .experience-item, .education-item {{
                        margin-bottom: 25px;
                        padding: 20px;
                        background: var(--bg-color);
                        border-radius: {theme['layout']['card_radius']};
                        border-left: 4px solid var(--secondary-color);
                        transition: transform 0.2s;
                    }}

                    .experience-item:hover, .education-item:hover {{
                        transform: translateX(5px);
                        border-left-color: var(--accent-color);
                    }}

                    .title {{
                        font-weight: bold;
                        color: var(--primary-color);
                        font-size: 18px;
                        margin-bottom: 5px;
                    }}

                    .date {{
                        color: var(--secondary-color);
                        font-style: italic;
                        margin: 5px 0;
                        font-size: 14px;
                    }}

                    ul {{
                        margin: 15px 0;
                        padding-left: 20px;
                    }}

                    li {{
                        margin-bottom: 8px;
                        position: relative;
                        color: #444;
                    }}

                    li::before {{
                        content: "•";
                        color: var(--accent-color);
                        font-weight: bold;
                        margin-right: 8px;
                    }}

                    .skills-list {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 12px;
                        list-style: none;
                        padding: 0;
                    }}

                    .skills-list li {{
                        background: var(--bg-color);
                        padding: 8px 15px;
                        border-radius: 20px;
                        font-size: 14px;
                        border: 1px solid var(--secondary-color);
                        transition: all 0.2s;
                    }}

                    .skills-list li:hover {{
                        background: var(--secondary-color);
                        color: white;
                    }}

                    .summary {{
                        font-size: 16px;
                        line-height: 1.8;
                        color: #444;
                        padding: 20px;
                        background: var(--bg-color);
                        border-radius: {theme['layout']['card_radius']};
                        margin-bottom: 25px;
                        border-left: 4px solid var(--accent-color);
                    }}

                    @media print {{
                        body {{
                            box-shadow: none;
                            padding: 0;
                        }}
                        .experience-item:hover, .education-item:hover {{
                            transform: none;
                        }}
                        .skills-list li:hover {{
                            background: var(--bg-color);
                            color: var(--text-color);
                        }}
                    }}

                    @media (max-width: 768px) {{
                        body {{
                            padding: 15px;
                        }}
                        .resume-header {{
                            padding: 30px 15px;
                        }}
                        .resume-header h1 {{
                            font-size: 28px;
                        }}
                    }}
                </style>
                """
                cleaned_text = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Modern Resume</title>
                    {style_template.format(theme=theme)}
                </head>
                <body>
                    {''.join(content)}
                </body>
                </html>
                """
            else:
                return jsonify({
                    'success': False,
                    'error': 'Could not find HTML content in response',
                    'raw_response': resume_text[:500]
                })
        
        if cleaned_text:
            return jsonify({
                'success': True, 
                'resume': cleaned_text.strip()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Empty response after cleaning'
            })

    except Exception as e:
        print("Exception Type:", type(e).__name__)
        print("Exception Details:", str(e))
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 