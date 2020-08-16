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
def features(face):
    image = face_recognition.load_image_file(path_to_face)
    #extracting feature vectors
    encoding = face_recognition.face_encodings(image);
    #binarization
    encoding= np.where(encoding>np.mean(encoding), 1, 0);
    return encoding;

#Generating Lock function and creates random key
def createLock(faceImage):
    #turning image into binarized feature vector
    A1=features(faceImage);
    
    #generating random Key
    randKey=np.random.choice([0, 1], size=(87,), p=[1./2, 1./2])

    #Reed-Solomon encoding
    RS=rs.RSCoder(127,87)
    code=RS.encode(randomKey)
    C1=np.where(np.zeros(128)>0, 1,0)
    for p in range(0,127):
        C1[p]=ord(code[p])

    #Creating Biometric lock
    bioLock=A1 ^ C1
    return bioLock, randKey;

def secondKey(secondFaceImage):
    global lock;
    #turning image into binarized feature vector
    A2=features(secondFaceImage)

    #xor lock with second feature vector
    Temp= A2 ^ lock
    C2=""
    for n in range(0,127):
        C2=C2+chr(Temp[n])

    #Getting key back
    key= RS.decode(C2)
    K=np.where(np.zeros(87)>0, 1,0)
    for m in range(0,len(key[0])):   
        K[m]=ord(key[0][m])
    return K;




#def encrypt(faceImage, file):
#    #generating lock and random key
#    result=createLock(faceImage)
#    lock=result[0]
#    randomKey=result[1]

#    #ENCRYPTION
#    backend = default_backend()

#    #padding key with zeros to reach 32 bytes
#    keyList=randomKey.tobytes();
#    paddedKey=keyList[:32]
#    iv = os.urandom(16) # initial vector of 16 bytes
#    cipher = Cipher(algorithms.AES(paddedKey), modes.CBC(iv), backend=backend)
#    encryptor = cipher.encryptor()
#    BUF_SIZE = 32768 # Read file in 32kb chunks 

#    #reading file
#    f= open('data.txt', 'rb')
#    encFile="data.enc"
#    f1=open(encFile,'wb')
#    try:
#        data = f.read(BUF_SIZE)
#        if not data:
#            encryptor.finalize()
#        ct=encryptor.update("a secret message")
#        f1.write(ct)
#    finally:
#        f.close()
#        f1.close();
#    return lock;

#def decrypt(secondFaceImage, file):
#    global lock;
#    #turning image into binarized feature vector
#    A2=features(secondFaceImage)

#     #xor lock with second feature vector
#    Temp= A2 ^ lock
#    C2=""
#    for n in range(0,127):
#        C2=C2+chr(Temp[n])

#    #Getting key back
#    key= RS.decode(C2)
#    K=np.where(np.zeros(87)>0, 1,0)
#    for m in range(0,len(key[0])):   
#        K[m]=ord(key[0][m])

#    #DECRYPTION

