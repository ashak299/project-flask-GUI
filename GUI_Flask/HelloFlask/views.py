import flask
from flask import Flask, render_template, request, redirect, redirect
import flask_uploads
from flask_uploads import UploadSet, DATA
import os
import HelloFlask
from HelloFlask import app
import werkzeug
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = 'HelloFlask/static/file_uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        "index.html",
        title = "Hello Flask",
        message = "Encrypting and Decrypting files, using face recognition",
        extensionMessage = "Firstly, use the webcam to take a snapshot of your face")

@app.route('/FileUpload')
def FileUpload():
    return render_template(
        "FileUpload.html",
        title= "Upload File",
        message= "Upload File to Encrypt",
        select= "Select a file to upload")


#file=UploadSet('file', DATA, default_dest=lambda x:'static/file_uploads/')

# Upload API
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        profile = request.files['file']
        profile.save(os.path.join(UPLOAD_FOLDER, secure_filename(profile.filename)))
        return redirect('http://localhost:5555/')
    return redirect('http://localhost:5555/NotUploaded')



@app.route('/NotUploaded')
def NotUploaded():
    return render_template(
        "NotUploaded.html")


if __name__ == '__main__':
    app.run(debug=True)