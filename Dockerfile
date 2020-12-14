FROM debian
RUN apt install cmake
ENV FLASK_APP=server.py
ENV FLASK_ENV=production
