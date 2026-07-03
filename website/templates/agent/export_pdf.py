export_pdf_template ="""
<!DOCTYPE html>
    <html>
        <head>
        <meta charset="UTF-8">
        <title>{{document_type}} - {{job_title}}</title>
        <style>
            body { font-family: 'Helvetica', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; padding: 20px; }
            h1, h2 { color: #1e3a8a; }
            .header { text-align: center; margin-bottom: 30px; }
            .content { font-size: 11pt; }
        </style>
        </head>
        <body>
        <div class="header">
            <h1>{{document_type}}</h1>
            <h2>{{job_title}}</h2>
        </div>
        <div class="content">
           {{content | safe}}
        </div>
        </body>
    </html>

"""