FROM python:3.10-alpine

ENV FLASK_APP webuzz.py
ENV FLASK_CONFIG production

RUN adduser -D webuzz
USER webuzz

WORKDIR /home/webuzz

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY webuzz.py config.py boot.sh ./

# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]