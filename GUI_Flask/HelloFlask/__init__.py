from flask import Flask
import os
app = Flask(__name__)

import HelloFlask.views



## Download API
#@app.route("/downloadfile/<filename>", methods = ['GET'])
#def download_file(filename):
#    return render_template('download.html',value=filename)
#@app.route('/return-files/<filename>')
#def return_files_tut(filename):
#    file_path = UPLOAD_FOLDER + filename
#    return send_file(file_path, as_attachment=True, attachment_filename='')

##Upload Image
#@app.route('/uploadfile', methods=['GET', 'POST'])
#def upload_image():
#    if request.method == 'POST':
#        # check if the post request has the file part
#        if 'file' not in request.files:
#            print('no file')
#            return redirect(request.url)
#        file = request.files['file']
#        # if user does not select file, browser also
#        # submit a empty part without filename
#        if file.filename == '':
#            print('no filename')
#            return redirect(request.url)
#        else:
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
#            print("saved image successfully")
#      #send file name as parameter to downlad
#            return redirect('/downloadfile/'+ filename)
#    return render_template('upload_file.html')