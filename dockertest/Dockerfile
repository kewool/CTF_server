FROM python:3.9

ENV PORT 3000

COPY . /app
COPY ./healthcheck.sh /etc
RUN rm -rf /app/healthcheck.sh
WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y net-tools

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod 777 /app/run.sh /app/main.py /etc/healthcheck.sh

HEALTHCHECK --interval=20m CMD /etc/healthcheck.sh

ENTRYPOINT /app/run.sh

EXPOSE 3000