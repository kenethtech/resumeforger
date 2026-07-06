
from flask import Blueprint, jsonify, request, render_template_string
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import login_required
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .config import Config
from .models import Generation
from . import db
from website.templates.agent.export_pdf import (export_pdf_template)
from .generate_pdf import generate_pdf
import markdown



agent = Blueprint('agent', __name__)

@agent.route('/generate', methods=['POST'])
@jwt_required()
@login_required
def generate_content():
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Kindly fill all the fields'}), 401
        
        job_title = data['job_title']
        full_name = data['full_name']
        email = data['email']
        phone_number = data['phone_number']
        job_description = data['job_description']
        education = data['education']
        user_background = data['experience']
        document_type = data['document_type']
        referees = data.get('referees', '')
        certifications = data.get('certifications', '')
        template_style = data.get('template_style', 'Professional')

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=Config.GROQ_API_KEY,
            temperature=0.65
        )
        resume_prompt = PromptTemplate.from_template("""
        You are a professional resume writer and career coach.
                                                     
        Job Title: {job_title}
        Job Description: {job_description}
        
        Full Name: {full_name}
        Email: {email}
        Phone Number: {phone_number}
        Education: {education}
        Certifications: {certifications}
                
        User Background: {user_background}
        Referees: {referees}
                            
        Document Type: {document_type}
        Template Style: {template_style}
                                                    
        Create a highly tailored, ATS-friendly, and visually appealing {document_type} using the **{template_style}** style.

        Key instructions:
            - Match keywords from the job description
            - Use strong action verbs and quantify achievements
            - Follow the chosen template style strictly
            - Keep it professional and impactful

        Return only the final formatted document content."""
        )

        parser = StrOutputParser()

        chain = resume_prompt | llm | parser

        result = chain.invoke({
            "job_title": job_title,
            "job_description": job_description,
            "full_name": full_name,
            "email": email,
            "phone_number": phone_number,
            "education": education,
            "user_background": user_background,
            "document_type": document_type,
            "referees": referees,
            "certifications": certifications,
            "template_style": template_style
        })

        score = 80

        gen = Generation(
            user_id= current_user_id,
            job_title= job_title,
            document_type= document_type,
            template_style= template_style,
            content= result,
            ats_score= score
        )
        db.session.add(gen)
        db.session.commit()

        return jsonify({
           'content': result,
           'document_type': document_type,
           'job_title': job_title,
           'template_style': template_style,
        })

    
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({
            'error': str(e)
        }), 404


@agent.route('/export-pdf', methods=['POST'])
@jwt_required()
@login_required
def export_pdf():
    try:
        data = request.get_json()
        content = data.get('content')
        job_title = data.get('job_title', 'Resume')
        document_type = data.get('document_type', 'Document')
        template_style = data.get('template_style', 'Professional')

        if not content:
            return jsonify({'error': 'No content provided'}), 405
        
        css_styles = {
            "Professional": """
                body { font-family: 'Georgia', serif; line-height: 1.7; color: #222; }
                h1 { color: #1e3a8a; border-bottom: 2px solid #1e3a8a; }
                h2 { color: #334155; border-bottom: 1px solid #e2e8f0; }
            """,
            "Modern": """
                body { font-family: 'Helvetica', Arial, sans-serif; line-height: 1.6; }
                h1 { color: #0ea5e9; letter-spacing: -1px; }
                h2 { color: #0369a1; }
                .section { border-left: 4px solid #0ea5e9; padding-left: 15px; }
            """,
            "Executive": """
                body { font-family: 'Times New Roman', serif; line-height: 1.8; }
                h1 { color: #1e2937; font-size: 28px; }
                h2 { color: #334155; text-transform: uppercase; letter-spacing: 1px; }
            """,
            "Creative": """
                body { font-family: 'Helvetica', sans-serif; line-height: 1.6; }
                h1 { color: #7c3aed; }
                h2 { color: #6b21a8; }
                .highlight { background: #f3e8ff; padding: 2px 8px; border-radius: 4px; }
            """,
            "Minimalist": """
            body { font-family: 'Arial', sans-serif; line-height: 1.7; }
            h1, h2 { color: #1f2937; }
            hr { border: none; border-top: 1px solid #e5e7eb; margin: 20px 0; }
            """,
            "Technical": """
                body { font-family: 'Courier New', monospace; line-height: 1.5; }
                h1 { color: #1e40af; }
                h2 { color: #3b82f6; }
                code { background: #f1f5f9; padding: 2px 6px; border-radius: 3px; }
            """
        }

        selected_css = css_styles.get(template_style, css_styles['Professional'])
        
        html_content = markdown.markdown(content)
        
        #Html template for pdf
        html_template = render_template_string(export_pdf_template, document_type=document_type, job_title=job_title, content=html_content, selected_css=selected_css)

        #Generate PDF
        response = generate_pdf(html_template, document_type, job_title)

        return response


    

    except Exception as e:
        return jsonify({
            'error': str(e)
        })
