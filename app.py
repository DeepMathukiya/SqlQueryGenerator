import google.generativeai as genai
from flask import Flask, render_template, request
import mysql.connector

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="Query_Generator"
    )

conn = connect_to_database()
c = conn.cursor() 
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS Responses (
                    response_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    promt varchar(255),
                    response varchar(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ); ''')
    conn.commit()


app = Flask(__name__)

@app.route('/')
def hello_world():
    c.execute('''SELECT * FROM Responses''')
    data = c.fetchall()
    return render_template('index.html',data=data)



@app.route('/predict' , methods=['GET','POST'])
def SQL_Generator():
     if request.method == 'POST':
        question = request.form['question']
        response = get_sql(question)
        c.execute('''INSERT INTO Responses (promt, response) VALUES (%s,%s)''', (question, response) )
        conn.commit()
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
    create_tables()
    app.run(host='0.0.0.0',port='7000') 