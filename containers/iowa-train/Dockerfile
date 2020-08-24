FROM python:3.8-buster

COPY requirements.txt /scripts/requirements.txt

RUN pip install -r /scripts/requirements.txt && \
    ipython kernel install --user

COPY train.ipynb /scripts/train.ipynb
COPY train.sh /scripts/train.sh

# For local test, mount data as a volume
# docker run -v path/to/local/data_train.csv:/data_train.csv tag

# Directly running papermill.  This works if the path for complete.ipynb exists,
# but KFP does not guarantee that for outputPath files
# ENTRYPOINT [ "papermill", "/scripts/train.ipynb" ]
# CMD ["complete.ipynb", \
#     "-p",  "data",  "data_train.csv", \
#     "-p",  "output_model",  "model.joblib", \
#     "-p",  "svm_gamma",  "0.1", \
#     "-p",  "svm_c",  "100" \
#     ]

ENTRYPOINT [ "bash", "/scripts/train.sh", "--notebook", "/scripts/train.ipynb" ]
CMD ["--output_notebook", "complete.ipynb", \
     "--data",  "data_train.csv", \
     "--output_model",  "model.joblib", \
     "--param_file",  "params.yml", \
     ]
