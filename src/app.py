from flask import Flask, request, redirect, send_file, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
import tarfile
import uuid

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'txt', 'png', 'tar', 'jpg', 'jpeg', 'gif'}  # 허용된 파일 확장자

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 업로드 파일을 files에 저장함
app.secret_key = "LI3CyLCkj5iEOWNLv0zV8RmqRsM5jK"

def allowed_file(filename):  # 파일 확장자 확인 함수
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')  # main_page

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400  # 파일이 아닐 경우
    
    file = request.files['file']
   
    if "uid" not in session:
        session["uid"] = str(uuid.uuid4())  # 세션에 uid가 없으면 새로 생성
    uid = session["uid"]
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], uid)
    os.makedirs(user_folder, exist_ok=True)  # 사용자 폴더 생성

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        
        try:
            if tarfile.is_tarfile(file_path):
                with tarfile.open(file_path, 'r') as tar:
                    tar.extractall(path=user_folder)  # 사용자 폴더에 압축 해제
                os.remove(file_path)  # 압축 해제 후 원본 tar 파일 삭제
            #return jsonify({'success': 'Files uploaded', 'uid': uid})  # 업로드 성공
            return redirect('/')
        except tarfile.TarError as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'File type not allowed'}), 400  # 허가되지 않은 파일일 때

@app.route('/api/access/<path:filename>')
def access_file(filename):
    if '..' in filename or '/' in filename:  # 경로 침입 방지
        return jsonify({'error': 'File not found'}), 404
    
    if "uid" not in session:
        return jsonify({'error': 'File not uploaded'}), 404
    uid = session["uid"]
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uid, filename)
    print("**********file_path************ : ", file_path)  # 경로 확인용 출력
    print("**********getcwd************ : ", os.getcwd())
    print("**********listdir************ : ", os.listdir())
    
    if os.path.isfile(file_path):
        print("**********HERE************ : ")
        return send_file(file_path)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/directory')
def list_files():
    if "uid" not in session:
        return jsonify({'error': 'File not uploaded'}), 404
    uid = session["uid"]
    
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], uid)
    if os.path.exists(user_folder):
        files = os.listdir(user_folder)
        return jsonify({'files': files})
    return jsonify({'error': 'User folder not found'}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
