FROM python:3.7-slim

# pip install
COPY requirements.txt /scripts/requirements.txt
RUN pip install -r /scripts/requirements.txt

# only for local testing
COPY registerartifacts.py /scripts/registerartifacts.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/registerartifacts.py" ]
