import os
import fitz  # PyMuPDF
import google.generativeai as genai
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# --- Modern Key Management ---
# For local development, we use a .env file.
# In production (Phase 2+), this will be replaced with AWS Secrets Manager.
try:
    api_key = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
except KeyError:
    # This error will be raised if the API key is not set.
    model = None
    print("ERROR: GEMINI_API_KEY environment variable not set.")
except Exception as e:
    model = None
    print(f"An error occurred during Gemini configuration: {e}")

def summarize_with_gemini(text):
    """Calls the Gemini API to summarize the given text."""
    if model is None:
        return "Gemini model is not configured. Please check your API key."
    
    prompt = f"Please provide a concise summary of the following text:\n\n{text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while calling the Gemini API: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    error = None
    
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            error = "No file part in the request. Please select a file."
            return render_template('index.html', error=error), 400
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            error = "No file selected. Please choose a PDF file to upload."
            return render_template('index.html', error=error), 400

        if file and file.filename.endswith('.pdf'):
            try:
                # Use PyMuPDF to open the file stream and extract text
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                extracted_text = "".join(page.get_text() for page in pdf_document)
                
                if extracted_text.strip():
                    summary = summarize_with_gemini(extracted_text)
                else:
                    error = "Could not extract any text from the uploaded PDF."

            except Exception as e:
                error = f"An error occurred while processing the PDF: {e}"
        else:
            error = "Invalid file type. Please upload a PDF file."

    return render_template('index.html', summary=summary, error=error)

if __name__ == '__main__':
    # The debug=True flag is useful for development as it provides detailed error pages
    # and automatically reloads the server when you make code changes.
    app.run(host='0.0.0.0', port=5000, debug=True)