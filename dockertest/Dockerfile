FROM python:3.9

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 777 /app/run.sh /app/main.py
ENTRYPOINT /app/run.sh

EXPOSE 3000