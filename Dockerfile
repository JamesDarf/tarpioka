
FROM --platform=linux/amd64 sanicframework/sanic:latest-py3.11

WORKDIR /chal
COPY flag ./
COPY ./src/ /chal/
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["sanic", "server", "-H", "0.0.0.0"]
