from flask import Flask, render_template, request, send_file
import pdfplumber
import pandas as pd
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
load_dotenv()


@app.route('/')
def index():
    return render_template('index.html')  # This template should have a file upload form

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return "No file part", 400
    file = request.files['pdf']
    if file.filename == '':
        return "No selected file", 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Extract text and tables from PDF
    data = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        data.append(row)
            else:
                lines = page.extract_text().split('\n')
                for line in lines:
                    data.append([line])  # wrap in list to keep CSV structure

    # Convert to DataFrame and save as CSV
    df = pd.DataFrame(data)
    csv_file = os.path.join(UPLOAD_FOLDER, filename.replace(".pdf", ".csv"))
    df.to_csv(csv_file, index=False, header=False)

    return send_file(csv_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
