export_pdf_template ="""
<!DOCTYPE html>
    <html>
        <head>
        <meta charset="UTF-8">
        <title>{{document_type}} - {{job_title}}</title>
        <style>
            body { max-width: 800px; margin: 0px auto; padding: 20px; {{selected_css}} }
            h1 { font-size: 26px; margin-bottom: 5px; }
            h2 { font-size: 18px; margin-top: 25px; }
            ul { padding-left: 20px; }
            li { margin-bottom: 8px; }
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