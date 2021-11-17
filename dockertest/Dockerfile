FROM python:3.9

COPY . /app
WORKDIR /app

RUN apt-get install -y net-tools

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 777 /app/run.sh /app/main.py /app/healthcheck.sh

HEALTHCHECK --interval=20m CMD ./healthcheck.sh

ENTRYPOINT /app/run.sh

EXPOSE 3000