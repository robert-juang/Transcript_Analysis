from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

import re
import json
import openai 
from pdfreader import PDFDocument, SimplePDFViewer
# from dotenv import load_dotenv

# load_dotenv()

application = Flask(__name__)
application.config["UPLOAD_FOLDER"] = "./static/pdf"
print(os.environ) 
application.secret_key = os.environ.get("app_secret")
openai.api_key = os.environ.get("openai_API")

@application.route("/")
@application.route("/home") 
def main():
    filestate = None
    filename = session.get('filename', "")  # get the filename from the session, if it's not set, use 'default.pdf'
    summary = session.get('summary', "")
    classes = session.get('classes', "")
    rec = session.get('recommendations', "") 
    
    if filename != "":
        filestate = True
    return render_template('home.html', filestate=filestate, filename=filename, summary=summary, classes=classes, recommendation=rec) 

@application.route("/about") 
def about():
    return "Hello about page"

@application.route('/upload-transcript', methods=['POST'])
def upload_transcript():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # If the user does not select a file, the browser might
    # submit an empty file without a filename.
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        session['filename'] = filename  # store the filename in the session
        file.save(os.path.join(application.config["UPLOAD_FOLDER"], filename))
    
    #call openai api here 
    filename = f"./static/pdf/{filename}"
    fd = open(filename, "rb")
    doc = PDFDocument(fd)
    viewer = SimplePDFViewer(fd)
    old = [] 
    for index, canvas in enumerate(viewer):
        page_strings = canvas.strings
        old.append(page_strings)  

    data = [item for sublist in old for item in sublist]

    viewer.render()

    # create a chat completion for summary
    chat_completion_summary = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Given the following data about the transcript of a university student, generate a summary for the student's performance. Write the summary in a second person tone using you, your, yours, yourself, yourselves. Here's the data: {data}"}])

    # print the chat completio
    summary = chat_completion_summary.choices[0].message.content
    print(summary) 
    summary = re.sub("'", "", summary)
    print(summary) 
    session['summary'] = summary  # store the filename in the session

    # create a chat completion for summary
    chat_completion_classes = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"""Given the following data about the transcript of a university student, 
                    please generate two lines with the student's best and worst performing class. In the case where the students have multiple classes with grades tied for best grades choose the class which more closely relates to their major.
                    Please use the following format and fill in the blank for the information surrounded by []. 
                    Format:                                                                          
                    Your best class is [classname] with a letter grade of [letter grade], which is taken during [semester].
                    Your worst class is [classname] with a letter grade of [letter grade], which is taken during [semester].                                                                   
                    Here's the data: {data}"""}])

    # print the chat completio
    classes = chat_completion_classes.choices[0].message.content
    
    session['classes'] = classes  # store the filename in the session

    chat_completion_recommendations = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"""Given the following data about the transcript of a university student, 
                    please generate a single sentence recommendation for the student based on the prompt below. 
                    The recommendations should involve one of the sample sentences from the following:
                        1. "Based on your major, you should look into [a couple of career paths related to the person's major and not including the classes they've taken]. 
                        2. "Because you took [choose a class], this field might interest you: [a couple of career fields related to class taken]    
                        3. "You did well in [class the student did well in], you should look into [a couple of career fields which is related to class taken].                                                                                                                                                                                                                      
                    please pick one of the three lines to output and fill in the blanks inside the information inside the brackets according to the data provided. 
                                                                                                                                                                    
                    Here's the data: {data}"""}])

    # print the chat completio
    recommendations = chat_completion_recommendations.choices[0].message.content
    
    session['recommendations'] = recommendations  # store the filename in the session

    chat_completion2 = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": 
        f"Using the data: {data} Can you now give me a summary of the student's performance in JSON format? Reply in json with this format:" + """                  
            {
                student_Name: "Insert Data here",
                student_ID:"Insert Data here",
                University:"Insert Data here",
                ap_credit: {
                    class: ["Insert Classes here"],
                    credit: ["Insert credit for class here"],
                    test_total: "insert data here"
                }
                semesters: {
                    fall_2019: {
                        college: "insert college info here",
                        degree: "insert degree info here",
                        major: "insert major info here",
                        classes:{
                            {
                                name = "insert name of class here", 
                                number = "Insert class number here like ECON-UA 1 - 001",
                                grade = "insert numerical grade here",
                                letter_grade = "insert letter grade here"
                            },
                            {
                                ... ("insert more classes based on pdf")
                            }
                        },
                        current_GPA: "insert current gpa here",
                        cumulative_GPA: "insert culumative gpa here",
                    },
                    ...{"insert more semesters here"}
                }
            }

            }
            }                                                               
            """}])
     # print the chat completio
    jsonSummary = chat_completion2

    print(jsonSummary) 
    
    session['json'] = jsonSummary.choices[0].message.content  # store the filename in the session

    return redirect(url_for('main'))

#this is for the future when I code in new things for the report instead of just the
@application.route('/upload-report', methods=['POST'])
def upload_report():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    # If the user does not select a file, the browser might
    # submit an empty file without a filename.
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        session['filename'] = filename  # store the filename in the session
        file.save(os.path.join(application.config["UPLOAD_FOLDER"], filename))
    
    #call openai api here 
    filename = f"./static/pdf/{filename}"
    fd = open(filename, "rb")
    doc = PDFDocument(fd)
    viewer = SimplePDFViewer(fd)
    old = [] 
    for index, canvas in enumerate(viewer):
        page_strings = canvas.strings
        old.append(page_strings)  

    data = [item for sublist in old for item in sublist]

    viewer.render()

    # create a chat completion
    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": f"Given the following data about the transcript of a university student, generate a summary for the student's performance.  {data}"}])

    # print the chat completio
    summary = chat_completion.choices[0].message.content
    
    session['summary'] = summary  # store the filename in the session

    chat_completion2 = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": 
        f"Using the data: {data} Can you now give me a summary of the student's performance in JSON format? Reply in json with this format:" + """                  
            {
                student_Name: "Insert Data here",
                student_ID:"Insert Data here",
                University:"Insert Data here",
                ap_credit: {
                    class: ["Insert Classes here"],
                    credit: ["Insert credit for class here"],
                    test_total: "insert data here"
                }
                semesters: {
                    fall_2019: {
                        college: "insert college info here",
                        degree: "insert degree info here",
                        major: "insert major info here",
                        classes:{
                            {
                                name = "insert name of class here", 
                                number = "Insert class number here like ECON-UA 1 - 001",
                                grade = "insert numerical grade here",
                                letter_grade = "insert letter grade here"
                            },
                            {
                                ... ("insert more classes based on pdf")
                            }
                        },
                        current_GPA: "insert current gpa here",
                        cumulative_GPA: "insert culumative gpa here",
                    },
                    ...{"insert more semesters here"}
                }
            }

            }
            }                                                               
            """}])
     # print the chat completio
    jsonSummary = chat_completion2

    print(jsonSummary) 
    
    session['json'] = jsonSummary.choices[0].message.content  # store the filename in the session

    
    # while (jsonSummary.choices[0].finish_reason == "length"):


    return redirect(url_for('main'))

if __name__ == "__main__":
    session['summary'] = "no file uploaded yet"
    application.run(debug=True)
    
    application.secret_key = 'super secret key'
    application.config['SESSION_TYPE'] = 'filesystem'

    session.init_app(application)



