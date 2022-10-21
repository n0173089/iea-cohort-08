FROM python:3.8-alpine
# TODO: Copy application files into container
COPY . /app
# TODO: Install python3 and python3-pip, hint "apt-get install python3 python3-pip"
# RUN apk update
# RUN apk add python3 python3-pip 
# TODO: Install required python libraries
RUN pip install -r /app/requirements.txt 
# TODO: Have the container expose port 8080
EXPOSE 8080
CMD python3 /app/app.py
