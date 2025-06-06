#FROM ubuntu:latest
#LABEL authors="clara"

#ENTRYPOINT ["top", "-b"]

FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=run.py

CMD ["flask", "run", "--host=0.0.0.0"]