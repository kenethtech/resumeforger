from playwright.sync_api import sync_playwright
import tempfile
import os
from flask import make_response


def generate_pdf(html_template, document_type, job_title):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        pdf_path = temp_pdf.name

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            page.set_content(html_template, wait_until='networkidle')
            page.pdf(
                path= pdf_path,
                format= 'A4',
                print_background= True,
                margin= {
                    'top': '20mm',
                    'bottom': '20mm',
                    'left': '15mm',
                    'right': '15mm'
                },  
            )

            browser.close()
        
        with open(pdf_path, 'rb') as f:
            pdf = f.read()
        
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{document_type}_{job_title}.pdf"'
        
        return response
    
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
