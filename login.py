from sanic import Sanic, json, redirect, file
from sanic.response import text
from sanic.request import Request
from auth import protected, protected_sync
from random import randbytes
from uuid import uuid4
from hashlib import md5
from util import validate
from urllib.parse import unquote
import os
import jwt
import aiosqlite
import io
import tarfile

ABSOLUTE_FILE_PATH = os.path.abspath("./files")
app = Sanic("TarchiveDrive")

app.config.SECRET = randbytes(30)
app.config.SALT = b'DAMCTF2024'

# serve single page web-app frontend
app.static("/", "./dist")
@app.get("/")
async def hello_world(request: Request) -> text:
    return redirect("/index.html")



@app.before_server_start
async def attach_db(app, loop):
    app.ctx.db = 'users.db'
    # Initialize the DB w/ user table
    async with aiosqlite.connect(app.ctx.db) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS "USERS" (
	            "user_id"	INTEGER UNIQUE,
	            "username"	TEXT UNIQUE,
	            "password"	TEXT,
	            "folder"	TEXT UNIQUE,
	            PRIMARY KEY("user_id")
            );''')
    

# login
@app.post("/api/signup")
async def signup_handler(request: Request) -> json:
    if not ('username' in request.json and 'password' in request.json):
        return json({"error": "Malformed request body, must include \"username\" and \"password\" fields!"}, status=400)
    
    username = request.json['username']
    password = request.json['password']

    if validate(password, type(''), 3) == False:
        return json({"error": "password attribute must be a string with at least 3 characters"}, status=400)
    if validate(username, type(''), 1) == False:
        return json({"error": "username attribute must be a string of length > 0"}, status=400)

    # generate folder name
    folder = str(uuid4())

    password_hash = md5(bytes(password, encoding='utf-8')+request.app.config.SALT).hexdigest()

    try:
        # make user folder
        os.mkdir(os.path.join('files',folder)) 
        # make sql entry
        async with aiosqlite.connect(app.ctx.db) as db:
            await db.execute('INSERT INTO USERS (username, password, folder) VALUES (?,?,?)', [username, password_hash, folder])
            await db.commit()
    except aiosqlite.DatabaseError as err:
        return json({"error": err}, status=500)
    # small brain moment
    except FileExistsError:
        return json({"error": "Redundant UUID folder name generated; I suck at coding. Try this request again, it will probably work."}, status=500)
    
    return json({"success": "account created"}, status=201)

@app.post("/api/login")
async def login_handler(request: Request) -> json:
    if not ('username' in request.json and 'password' in request.json):
        return json({"error": "Malformed request body, must include \"username\" and \"password\" fields!"}, status=400)
    
    username = request.json['username']
    password = request.json['password']
    
    if validate(password, type(''), 3) == False:
        return json({"error": "password attribute must be a string with at least 3 characters"}, status=400)
    if validate(username, type(''), 1) == False:
        return json({"error": "username attribute must be a string of length > 0"}, status=400)
    
    folder = ''

    password_hash = md5(bytes(password, encoding='utf-8')+request.app.config.SALT).hexdigest()

    async with aiosqlite.connect(app.ctx.db) as db:
        async with db.execute('SELECT user_id, username, password, folder FROM USERS WHERE username = ? and password = ?', [username, password_hash]) as cursor:
            row = await cursor.fetchone()
            if row == None:
                return json({"error": "wrong password or username"}, status=400)
            folder = row[3]

    token = jwt.encode({
        "username": username,
        "password": password,
        "folder": folder,
    }, request.app.config.SECRET)

    return json({
        "success": "login successful",
        'jwt': token,
        "username": username
    }, status=200)

@app.post("/api/upload")
@protected_sync
def handle_tar_upload(request: Request):
    # extract user files
    tarbytes = io.BytesIO(request.body)
    try:
        with tarfile.open(fileobj=tarbytes, mode='r') as file_upload:
            file_upload.extractall(os.path.join("files", request.ctx.user['folder']))
    except tarfile.ReadError as err:
        return json({'error': str(err)}, status=400)
    return json({"success": "files uploaded"})

@app.get("/api/access/<filename>")
@protected
async def handle_file_access(request: Request, filename):
    filename = unquote(filename)
    file_path = os.path.join("files", request.ctx.user['folder'], filename)
    file_path = os.path.abspath(os.path.normpath(file_path))
    if file_path.startswith(ABSOLUTE_FILE_PATH):
        return await file(file_path)
    return await json({"error": "file not found"}, status=404)

@app.get("/api/directory")
@protected
async def list_userfiles(request: Request):
    return json({"files": os.listdir(os.path.join("files", request.ctx.user['folder']))})
