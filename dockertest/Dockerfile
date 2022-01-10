FROM python:3.9

ENV PORT 3000

COPY . /app
WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y net-tools

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 755 /app/run.sh /app/main.py /app/.______.sh

HEALTHCHECK --interval=10m CMD /app/.______.sh

ENTRYPOINT /app/run.sh

EXPOSE 3000