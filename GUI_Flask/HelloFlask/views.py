import flask
from flask import Flask, render_template, request, redirect, send_from_directory
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
import pickle

#-------------------------face recognition and encryption-----------------------------
import face_recognition
import random
import numpy as np
import unireedsolomon as rs
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

#FUNCTIONS
#reed solomon coder
RS=rs.RSCoder(128,90)

#takes in a numpy ndarray and outputs a 32 byte value
def randIntTo32(x):
    #padding with 0s to reach 256 int values
    padding = 32 * 8 - len(x)
    zero_padding = np.zeros(padding).astype(int)
    padded_arr = np.concatenate((x, zero_padding)).astype(str)

    #dividing these 256 values into 32 sub-arrays of size 8
    split_arr = np.split(padded_arr, 32)

    #making the 8 values of one subarray into a single string, one byte, and then converting to decimal
    int_arr = []
    for i in split_arr:
        int_arr.append(int(''.join(i), 2))
    
    #converting the the int array into a bytes with size 32 bytes
    bytes_key=bytes(int_arr)
    return bytes_key

#encryption function
def encrypt(key):
    backend = default_backend()
    #Padding key to 32 bytes
    k=randIntTo32(key)

    #Initalisation Vector
    iv = os.urandom(16)
    #saving iv
    ivFile=open("HelloFlask/static/encryption_folder/ivFile", 'wb')
    pickle.dump(iv, ivFile)
    ivFile.close()

    cipher = Cipher(algorithms.AES(k), modes.CTR(iv), backend=backend)
    encryptor = cipher.encryptor()
    BUF_SIZE = 1024 # Read file in 32kb chunks

    #encrypting
    #uploaded file
    file=os.listdir("HelloFlask/static/file_uploads")[0]
    filePath=os.path.join("HelloFlask/static/file_uploads", file)
    #encrypted file
    encFile="HelloFlask/static/encryption_folder/EncryptedFile.enc"
    f1 = open(encFile, 'wb')
    with open(filePath, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if (len(data)>0):
                pt = encryptor.update(data)
                f1.write(pt)
            else:
                break

    f.close()
    f1.close()
   
    return True;

#decryption function
def decrypt(key, iv):
    backend = default_backend()

    #Padding key to 32 bytes
    k=randIntTo32(key)

    cipher = Cipher(algorithms.AES(k), modes.CTR(iv), backend=backend)
    decryptor=cipher.decryptor()
    BUF_SIZE = 1024 # Read file in 32kb chunks

    fileName="HelloFlask/static/encryption_folder/EncryptedFile.enc"
    decFile="HelloFlask/static/encryption_folder/DecryptedFile.txt"
    f1 = open(decFile, 'wb')
    with open(fileName, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if (len(data)>0):
                pt = decryptor.update(data)
                f1.write(pt)
            else:
                break

    f.close()
    f1.close()

#Function used to verify that the key is the same
def areEqual(arr1, arr2, n):
    for j in range(0, n-1):
        if arr1[j] != arr2[j]:
            return False;
    return True;

#Function used to extract feature vectors and binarize
def features(path):
    try:
        image = face_recognition.load_image_file(path)
        #extracting feature vectors
        encoding = face_recognition.face_encodings(image)[0];
        #binarization
        arr=np.array(encoding)
        arr=np.where(arr>np.mean(arr), 1, 0);

        return arr;
    #no face detected
    except IndexError:
        res=['no', 'face', 'detected']
        return res;


#Generating Lock function and creates random key, then calls encrypt function
def createLock(path):
    #turning image into binarized feature vector
    A1=features(path);
    print(A1)

    #generating random Key
    randKey=np.random.choice([0, 1], size=(90,), p=[1./2, 1./2])

    #Reed-Solomon encoding    
    code=RS.encode(randKey)
    C1=np.where(np.zeros(128)>0, 1,0)
    for p in range(0,128):
        C1[p]=ord(code[p])

    #Creating Biometric lock
    bioLock=A1 ^ C1

    #encrypting file
    encrypt(randKey)

    return bioLock, randKey


#checks if the two images are a match, then calls decrypt function
def check(secondFacePath, randomKey, lock): 
    try:
        #turning image into binarized feature vector
        A2=features(secondFacePath)

        #xor lock with second feature vector
        Temp= A2 ^ lock
        C2=""
        for n in range(0,128):
            C2=C2+chr(Temp[n])

        #Getting key back using second feature vector
        #Reed- Solomon decoding
        key= RS.decode(C2)
        K=np.where(np.zeros(90)>0, 1,0)
        for m in range(0,len(key[0])):   
            K[m]=ord(key[0][m])

        print(K, flush=True)
        print(randomKey, flush=True)
       
        #check if equal
        if (areEqual(K, randomKey, len(randomKey))):
            #getting iv
            iv_file=open("HelloFlask/static/encryption_folder/ivFile", 'rb')
            initilisation_vector=pickle.load(iv_file)
            iv_file.close();

            #decrypting file
            decrypt(K, initilisation_vector)
            return True;
        else:
            print(" Fail", flush=True)
            return False;
    #this exception is thrown when the face is not a match
    except rs.RSCodecError:
        print("Not a match, over threshold: i.e result if the two faces are from different people", flush=True)
        return False;


#------------------------------------------------------------------------------------

#APP ROUTING
#decoding image from base 64 and saving it to file path
def getI420FromBase64(codec, path):
    base64_data = re.sub('^data:image/.+;base64,', '', codec)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    img.save(path)


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
    #checking image contains a face before proceeding
    img=features("HelloFlask/static/image_uploads/first_image.jpeg")
    if (isinstance(img[0], str)):
        return redirect("http://localhost:5555/NotUploaded")

    #uploading file if image is appropriate
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
        "NotUploaded.html",
        errorMsg = "Face not detected in image",
        explanation= "Make sure all your face is clearly shown")


#uploading face image
@app.route('/ImageUpload', methods=['GET', 'POST'])
def ImageUpload():
    if request.method == 'POST':
        faceImage=request.form.get('face');
        img=getI420FromBase64(faceImage, "HelloFlask/static/image_uploads/first_image.jpeg");
        return redirect('http://localhost:5555/FileUpload')
    return redirect('http://localhost:5555/NotUploaded')


#Creating Biometric Lock used in encryption /decryption and encrypts file
@app.route('/CreateLock')
def CreateLock():
    
    #generating random key and biometric lock from first face image
    #using this random key to encrypt the file
    lock,key=createLock("HelloFlask/static/image_uploads/first_image.jpeg");

    #Saving lock
    f=open("HelloFlask/static/encryption_folder/lock", 'wb')
    pickle.dump(lock, f)
    f.close()

    #saving key
    f1=open("HelloFlask/static/encryption_folder/randomKey", "wb")
    pickle.dump(key, f1)
    f1.close();

    return render_template(
        "CreateLock.html",
        encrypted = "File Encrypted")

#upload second image
@app.route('/SecondImage', methods=['GET', 'POST'])
def SecondImage():
    if request.method == 'POST':
        faceImage=request.form.get('face');
        getI420FromBase64(faceImage, "HelloFlask/static/image_uploads/second_image.jpeg");
        return redirect('http://localhost:5555/checking')
    return redirect('http://localhost:5555/NotUploaded')


#checks if second image  matches first -> if a match, decrypts file
@app.route('/checking')
def checking():
    #check if image contains a face before proceeding.
    img=features("HelloFlask/static/image_uploads/second_image.jpeg")
    #no face detected
    if (isinstance(img[0], str)):
        return redirect("http://localhost:5555/NotUploadedDecrypt")

    else:
        #get random key
        keyFile= open("HelloFlask/static/encryption_folder/randomKey", 'rb')
        original_key = pickle.load(keyFile)
        keyFile.close();
        #print(original_key,flush=True)
        #print(type(original_key), flush=True)


        #get lock
        lockFile=open("HelloFlask/static/encryption_folder/lock", 'rb')
        biometric_lock=pickle.load(lockFile)
        lockFile.close();
        #print(biometric_lock, flush=True)

        #check if two values are equal -> if equal, file is decrypted
        isSuccess=check("HelloFlask/static/image_uploads/second_image.jpeg", original_key, biometric_lock)

        if (isSuccess):
            print("SUCCESS", flush=True)
            #screen allows user to download decrypted file
            return render_template(
                "checking.html",
                success= "Success!")
        else:
            return redirect('http://localhost:5555/NotSuccessful')

#no face detected in second image
@app.route('/NotUploadedDecrypt')
def NotUploadedDecrypt():
    return render_template(
        "NotUploadedDecrypt.html",
        errorMsg= "No Face Detected in this image",
        explantion = "Make sure all your face is visible")

#redirects here if not a match
@app.route('/NotSuccessful')
def NotSuccessful():
    return render_template(
        "NotSuccessful.html",
        no_match= "Face was not a match, decryption not successful")

#clearing files
@app.route('/deleteFiles')
def deleteFiles():
        #clearing files
        os.remove("HelloFlask/static/image_uploads/first_image.jpeg")
        os.remove("HelloFlask/static/image_uploads/second_image.jpeg")
        os.remove("HelloFlask/static/encryption_folder/EncryptedFile.enc")
        os.remove("HelloFlask/static/encryption_folder/ivFile")
        os.remove("HelloFlask/static/encryption_folder/lock")
        os.remove("HelloFlask/static/encryption_folder/randomKey")
        os.remove("HelloFlask/static/encryption_folder/DecryptedFile.txt")

        file=os.listdir("HelloFlask/static/file_uploads")[0]
        filePath=os.path.join("HelloFlask/static/file_uploads", file)
        os.remove(filePath)

        return redirect('http://localhost:5555/')

if __name__ == '__main__':
    app.run(debug=True)


