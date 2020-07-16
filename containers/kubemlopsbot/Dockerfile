FROM python:3.7.4-slim-buster

COPY . /bot/
WORKDIR bot

RUN pip install -r requirements.txt --upgrade

ENV PYTHONUNBUFFERED=1

CMD ["python", "kubemlopsbotserver.py"]
