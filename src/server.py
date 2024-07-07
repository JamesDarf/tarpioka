from sanic import Sanic, json, redirect, file
from sanic.response import text
from sanic.request import Request
from urllib.parse import unquote
import os
import io
import tarfile

ABSOLUTE_FILE_PATH = os.path.abspath("./files")
app = Sanic("TarchiveDrive") #기반 제작

app.static("/", "./template")
@app.get("/")
async def hello_world(request: Request) -> text:
    return redirect("/index.html") #index.html

@app.post("/api/upload") #upload
def handle_tar_upload(request: Request):
    # extract user files
    tarbytes = io.BytesIO(request.body)
    try:
        with tarfile.open(fileobj=tarbytes, mode='r') as file_upload:
            file_upload.extractall(os.path.join("files")) #
    except tarfile.ReadError as err:
        return json({'error': str(err)}, status=400)
    return json({"success": "files uploaded"})

@app.get("/api/access/<filename>") # access
async def handle_file_access(request: Request, filename):
    filename = unquote(filename)
    file_path = os.path.join("files", filename) #
    file_path = os.path.abspath(os.path.normpath(file_path))
    if file_path.startswith(ABSOLUTE_FILE_PATH):
        return await file(file_path)
    return await json({"error": "file not found"}, status=404)

@app.get("/api/directory")
async def list_userfiles(request: Request):
    return json({"files": os.listdir(os.path.join("files"))}) #

