FROM python:3.7-slim

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt

COPY register.py /scripts/register.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/register.py" ]
