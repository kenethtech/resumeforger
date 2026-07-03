
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
        job_description = data['job_description']
        user_background = data['experience']
        document_type = data['document_type']

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=Config.GROQ_API_KEY,
            temperature=0.65
        )
        resume_prompt = PromptTemplate.from_template("""
        You are a senior career coach and expert resume writer.
                                                     
        Job Title: {job_title}
        Job Description: {job_description}
                
        User Background: {user_background}
                                                    
        Create a highly tailored, professional, and ATS-friendly {document_type} for this role.

        - Use strong action verbs
        - Quantify achievements where possible
        - Match keywords from the job description
        - Make it concise and impactful

        Return only the final document content.
        
        """)

        parser = StrOutputParser()

        chain = resume_prompt | llm | parser

        result = chain.invoke({
            "job_title": job_title,
            "job_description": job_description,
            "user_background": user_background,
            "document_type": document_type
        })

        score = 80

        gen = Generation(
            user_id= current_user_id,
            job_title= job_title,
            document_type= document_type,
            template_style= 'Professional',
            content= result,
            ats_score= score
        )
        db.session.add(gen)
        db.session.commit()

        return jsonify({
           'content': result,
           'document_type': document_type,
           'job_title': job_title
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

        if not content:
            return jsonify({'error': 'No content provided'}), 405
        
        html_content = markdown.markdown(content)
        
        #Html template for pdf
        html_template = render_template_string(export_pdf_template, document_type=document_type, job_title=job_title, content=html_content)

        #Generate PDF
        response = generate_pdf(html_template, document_type, job_title)

        return response


    

    except Exception as e:
        return jsonify({
            'error': str(e)
        })
