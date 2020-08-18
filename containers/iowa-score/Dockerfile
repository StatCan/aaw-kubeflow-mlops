FROM python:3.8-buster

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt && \
    ipython kernel install --user

COPY score.ipynb /scripts/score.ipynb
COPY score.sh /scripts/score.sh

# COPY data_train.csv data_train.csv
# For local test, mount data as a volume
# docker run -v path/to/local/data_train.csv:/test.csv -v path/to/local/model.joblib:/model.joblib tag
# ENTRYPOINT [ "papermill", "/scripts/score.ipynb" ]
# CMD ["complete.ipynb", \
# 	 "-p",  "data",  "test.csv", \
# 	 "-p",  "model",  "model.joblib", \
# 	 "-p",  "results_file_prefix",  "results" ]

ENTRYPOINT [ "bash", "/scripts/score.sh", "--notebook", "/scripts/score.ipynb" ]
CMD ["--output_notebook", "complete.ipynb", \
     "--data",  "test.csv", \
     "--model",  "model.joblib", \
     "--output_classification_report_filename",  "classification_report.csv", \
     "--output_f1_filename",  "f1.txt"]