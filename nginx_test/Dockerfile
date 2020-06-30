FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt -y install python3.8
RUN apt install -y ffmpeg
RUN apt-get install -y frei0r-plugins
RUN apt-get update
RUN apt-get -y install python3-pip

RUN mkdir pose_backend

COPY . /pose_backend

WORKDIR /pose_backend

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn","--bind","0.0.0.0:5000","wsgi"]

