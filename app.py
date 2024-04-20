import google.generativeai as genai
from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/predict' , methods=['GET','POST'])
def SQL_Generator():
     if request.method == 'POST':
        question = request.form['question']
        response = get_sql(question)
        return render_template('index.html', question=question, response=response)






def get_sql(question):
    genai.configure(api_key = "AIzaSyA7s9CKv8mZFnmb8h216cA_th-zXiC-vhM")
    # Set up the model
    generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
    ]
    model = genai.GenerativeModel(model_name = "gemini-pro",
                                generation_config = generation_config,
                                safety_settings = safety_settings)

    prompt_parts_1 = [
    "You are an expert in converting English questions to SQL code!",
    ]
    prompt_parts = [prompt_parts_1[0], question]
    response = model.generate_content(prompt_parts)
    return response.text



if __name__ == '__main__':
    app.run(host='0.0.0.0',port='7000') 