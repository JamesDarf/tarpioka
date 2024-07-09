from flask import Flask, request, redirect, send_file, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import tarfile
import io

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'txt', 'png', 'tar', 'jpg', 'jpeg', 'gif'} # 허용된 파일 확장자

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER #'업로드 파일을 files에 저장함.'

def allowed_file(filename): # 파일 확장자 확인 함수
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html') #main_page


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400 # 파일이 아닐 경우.
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            with tarfile.open(file_path, 'r') as tar:
                tar.extractall(path=app.config['UPLOAD_FOLDER']) # extractall
            # os.remove(file_path)  # 압축 해제 후 원본 tar 파일 삭제
            return jsonify({'success': 'Files uploaded'}) # 업로드 성공
        except tarfile.TarError as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'File type not allowed'}), 400 # 허가 되지 않을 파일일 때


@app.route('/api/access/<path:filename>')
def access_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #
    print("**********file_path************ : ",file_path) # check
    print("**********getcwd************ : ", os.getcwd())
    print("**********listdir************ : ", os.listdir())

    if os.path.isfile(file_path):
        return send_file(file_path)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/directory')
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({'files': files})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
