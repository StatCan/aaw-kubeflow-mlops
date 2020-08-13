FROM python:3.8-buster

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt && \
    ipython kernel install --user

COPY train.ipynb /scripts/train.ipynb

# COPY data_train.csv data_train.csv
# For local test, mount data as a volume
# docker run -v path/to/local/data_train.csv:/data_train.csv tag
ENTRYPOINT [ "papermill", "/scripts/train.ipynb" ]
CMD ["train_complete.ipynb", \
	 "-p",  "data",  "data_train.csv", \
	 "-p",  "output_model",  "model.joblib", \
	 "-p",  "svm_gamma",  "0.1", \
	 "-p",  "svm_C",  "100" \
	 ]
