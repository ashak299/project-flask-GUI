from flask import Flask
from HelloFlask import app
from flask import render_template

@app.route('/')
@app.route('/home')
def home():

    return render_template(
        "index.html",
        title = "Hello Flask",
        message = "Encrypting and Decrypting files, using face recognition",
        extensionMessage = "Files to be encrypted must have extension: .txt, .docx or .doc",
        select = "Select a file: ")
