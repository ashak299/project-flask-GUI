import flask
from flask import Flask, render_template, request, redirect
import flask_uploads
from flask_uploads import UploadSet, DATA
import os
import HelloFlask
from HelloFlask import app
import werkzeug
from werkzeug.utils import secure_filename
from base64 import b64decode
from PIL import Image
from io import BytesIO
import re, time, base64

#-----------face recognition and encryption-------------
import face_recognition
import random
import numpy as np
import unireedsolomon as rs
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

#FUNCTIONS
#Function used to verify that the key is the same
def areEqual(arr1, arr2, n):
    for j in range(0, n-1):
        if arr1[j] != arr2[j]:
            return False;
    return True;

#Function used to extract feature vectors and binarize
def features(path):
    image = face_recognition.load_image_file(path)
    #extracting feature vectors
    encoding = face_recognition.face_encodings(image);
    #binarization
    encoding= np.where(encoding>np.mean(encoding), 1, 0);
    return encoding;

#Generating Lock function and creates random key
def createLock(path):
    #turning image into binarized feature vector
    A1=features(path);
    print(A1)
    
    #generating random Key
    randKey=np.random.choice([0, 1], size=(87,), p=[1./2, 1./2])

    #Reed-Solomon encoding
    RS=rs.RSCoder(127,87)
    code=RS.encode(randKey)
    C1=np.where(np.zeros(128)>0, 1,0)
    for p in range(0,127):
        C1[p]=ord(code[p])

    #Creating Biometric lock
    bioLock=A1 ^ C1
    return bioLock, randKey;

def check(secondFacePath, randomKey, lock):

    #turning image into binarized feature vector
    A2=features(secondFacePath)
    print(A2, flush=True)
    #xor lock with second feature vector
    Temp= np.logical_xor(A2, lock)
    print(Temp, flush=True)
    C2=""
    for n in range(0,127):
        C2=C2+chr(Temp[n])

    #Getting key back
    key= RS.decode(C2)
    K=np.where(np.zeros(87)>0, 1,0)
    for m in range(0,len(key[0])):   
        K[m]=ord(key[0][m])

    #check if equal
    if (areEqual(K, randomKey, len(randomKey))):
        return true;
    else:
        return false;

#---------------------------------------------#

#Upload folders
UPLOAD_FOLDER = 'HelloFlask/static/file_uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

IMAGE_FOLDER='HelloFlask/static/image_uploads/'
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

#index page
@app.route('/')
@app.route('/home')
def home():
     return render_template(
        "index.html",
        title = "Hello Flask",
        message = "Encrypting and Decrypting files, using face recognition",
        extensionMessage = "Firstly, use the webcam to take a snapshot of your face, then press upload")

#file uploader page
@app.route('/FileUpload')
def FileUpload():
    return render_template(
        "FileUpload.html",
        title= "Upload File",
        message= "Upload File to Encrypt",
        fileType = "Files must have extension .txt, .doc or .docx",
        select= "Select a file to upload")

# Upload API
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        profile = request.files['file']
        profile.save(os.path.join(UPLOAD_FOLDER, secure_filename(profile.filename)))
        return redirect('http://localhost:5555/CreateLock')
    return redirect('http://localhost:5555/NotUploaded')


#displays when file has not been uploaded
@app.route('/NotUploaded')
def NotUploaded():
    return render_template(
        "NotUploaded.html")

#decoding image from base 64 and saving it to file path
def getI420FromBase64(codec, path):
    base64_data = re.sub('^data:image/.+;base64,', '', codec)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    img.save(path)

#uploading face image
@app.route('/ImageUpload', methods=['GET', 'POST'])
def ImageUpload():
    if request.method == 'POST':
        #print(request.form, flush=True);
        faceImage=request.form.get('face');
        getI420FromBase64(faceImage, "HelloFlask/static/image_uploads/first_image.jpeg");
        #faceImage= request.files['face']
        #filename='face_image';
        #f = open("HelloFlask/static/image_uploads/face_image.jpeg", "w")
        ##f.write(b64decode(faceImage))
        #f.write(faceImage)
        #f.close()
        #faceImage.save(os.path.join(IMAGE_FOLDER, secure_filename(faceImage.filename)))
        return redirect('http://localhost:5555/FileUpload')
    return redirect('http://localhost:5555/NotUploaded')



#Creating Lock
@app.route('/CreateLock')
def CreateLock():
    #get first image
    #first=Image.open("HelloFlask/static/image_uploads/first_image.jpeg");

    #generating random key and biometric lock from first face image
    lock,key=createLock("HelloFlask/static/image_uploads/first_image.jpeg");
    print(key, flush=True)
    #lock=result[0]
    #key=result[1]

    #save lock- write into python text file
    f=open("HelloFlask/static/encryption_folder/lock.txt", "w")
    for row in lock:
        np.savetxt(f,row);
    f.close();
    #save random key for checking later
    f1=open("HelloFlask/static/encryption_folder/randomKey.txt", "w")
    np.savetxt(f1,key);
    f1.close();

    return render_template(
        "CreateLock.html")



#redirect to web cam page 2
@app.route('/SecondImage', methods=['GET', 'POST'])
def SecondImage():
    if request.method == 'POST':
        faceImage=request.form.get('face');
        getI420FromBase64(faceImage, "HelloFlask/static/image_uploads/second_image.jpeg");
        return redirect('http://localhost:5555/FileUpload')
    return redirect('http://localhost:5555/NotUploaded')


@app.route('/checking')
def checking():
    #get random key
    original_key = np.loadtxt("HelloFlask/static/encryption_folder/randomKey.txt")
    print(original_key,flush=True)

    #get lock
    biometric_lock=np.loadtxt("HelloFlask/static/encryption_folder/lock.txt")
    print(biometric_lock, flush=True)
    isSuccess=check("HelloFlask/static/image_uploads/second_image.jpeg", original_key, biometric_lock)

    if isSuccess:
        return render_template(
            "checking.html")
    else:
        return redirect('http://localhost:5555/NotUploaded')


if __name__ == '__main__':
    app.run(debug=True)

