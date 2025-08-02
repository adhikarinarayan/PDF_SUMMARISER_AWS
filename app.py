import os
import fitz  # PyMuPDF
from google import genai
from flask import Flask, render_template, request
from dotenv import load_dotenv

# Load environment variables from the .env file for local development
load_dotenv()

app = Flask(__name__)



# --- Correct, Modern Client Initialization ---
# We will create the client once when the application starts.
try:
    # 1. Read our specific key from the environment and STRIP it of any whitespace.
    api_key = os.environ["GEMINI_API_KEY"]
    
    # 2. Instantiate the client, EXPLICITLY passing the API key to it.
    client = genai.Client(api_key=api_key)
    
    # 3. Define the model you want to use
    MODEL_NAME = "gemini-2.5-flash"
    
except KeyError:
    print("FATAL ERROR: GEMINI_API_KEY environment variable not set.")
    client = None
except Exception as e:
    print(f"An error occurred during Gemini client initialization: {e}")
    client = None

def summarize_with_gemini(text):
    """Calls the Gemini API to summarize the given text using the client."""
    if client is None:
        return "Gemini client is not initialized. Please check server logs."
    
    prompt = f"Please provide a concise summary of the following text:\n\n{text}"
    
    try:
        # 4. Use the client to generate content.
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
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
            error = "No selected file. Please choose a PDF file to upload."
            return render_template('index.html', error=error), 400

        if file and file.filename.endswith('.pdf'):
            try:
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
    app.run(host='0.0.0.0', port=5000, debug=True)