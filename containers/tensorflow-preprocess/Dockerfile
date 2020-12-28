FROM tensorflow/tensorflow:2.2.1

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt

COPY data.py /scripts/data.py

# will be overwritten by kf pipeline
ENTRYPOINT [ "python", "/scripts/data.py" ]
