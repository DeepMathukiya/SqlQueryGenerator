import google.generativeai as genai
from flask import Flask, render_template, request,url_for,redirect
import mysql.connector
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()
    

def connect_to_database():
    return mysql.connector.connect(
        host=os.getenv('host'),
        user=os.getenv('user'),
        password=os.getenv('password'),
        database=os.getenv('database')
        )

conn = connect_to_database()
c = conn.cursor() 
def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS Responses (
                    response_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    promt text,
                    response text,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ); ''')
    conn.commit()

create_tables()

app = Flask(__name__, static_url_path='/static') 

@app.route('/')
def hello_world():
    c.execute('''SELECT * FROM Responses order by created_at desc;''')
    data = c.fetchall()
    return render_template('index.html',data=data)



@app.route('/predict' , methods=['GET','POST'])
def SQL_Generator():
     if request.method == 'POST':
        question = request.form['question']
        checkbox_value = request.form.get('myCheckbox')
        if checkbox_value == 'on':
            c.execute('''SELECT response FROM Responses order by created_at desc limit 1;''')
            data2 = c.fetchall()
            question2 = [(question + 'Refrence below query if it has any error or missing information for to update then point it out' + str(row)) for row in data2]
            question2= str(question2)
        else :
            question2 = question

        response = get_sql(question2)
           
        c.execute('''INSERT INTO Responses (promt, response) VALUES (%s,%s)''', (question, response) )
        conn.commit()
        c.execute('''SELECT * FROM Responses order by created_at desc;''')
        data = c.fetchall()
        return render_template('index.html', question=question, response=response,data=data)
     else:
         return hello_world()


@app.route('/delete')
def delete():
    id = request.args.get('id') 
    c.execute('''DELETE FROM Responses WHERE response_id = %s;''', (id,))
    conn.commit()
    return redirect(url_for('hello_world'))


def get_sql(question):
    genai.configure(api_key=os.getenv('api_key'))
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
        "You are an expert in converting English questions to SQL code if given query has major error then please tell this error! ",]
    prompt_parts = [prompt_parts_1[0], question]
    response = model.generate_content(prompt_parts)
    return response.text



if __name__ == '_main_':
    configure()
    app.run(host='0.0.0.0',port='1000')