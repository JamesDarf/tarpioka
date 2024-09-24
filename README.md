# BubbleTea
CVE-2007-4559
“.tar”를 이용한 디렉토리 탐색 취약점으로 ../../flag

## path
--------------------
```
BubbleTea/
├── Dockerfile
├── flag
├── requirements.txt
└── src
    ├── files
    ├── template
    │   └── index.html
    └── app.py
```

### Current Building Instructions
- check docker
docker ps
docker images

docker build -t tarpioka
docker run -d -it --name tarpioka -p 13680:8000 tarpioka

docker ps

- stop and remove docker 
docker stop tarpioka
docker rm tarpioka
docker rmi tarpioka


### Run attack script



## patch
- 07/14
1. path Traversal
file name 인자에 '..', '/'가 포함된 문자열 벤

2. 세션별로 업로드 폴더 제작

3. 로그 남기기 추가

