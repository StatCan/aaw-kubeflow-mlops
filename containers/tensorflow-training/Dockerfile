FROM tensorflow/tensorflow:2.2.1

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt

COPY train.py /scripts/train.py

ENTRYPOINT [ "python", \
            "/scripts/train.py", \
            "-d", "data/train", \
            "-e", "10", \
            "-b", "32", \
            "-l", "0.0001", \
            "-o", "model", \
            "-f", "train.txt" ]
