FROM python:3.7.4-buster
RUN apt update
ARG INSTANCE
ENV FLASK_APP=server.py
ENV FLASK_ENV=production

WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN apt-get install ffmpeg libsm6 libxext6  -y

# Installing requirements for application.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "flask", "run", "-h", "0.0.0.0" ]
