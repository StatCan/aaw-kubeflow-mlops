FROM python:3.7-buster

RUN python3 -m pip install --upgrade pip

COPY register.py /scripts/register.py
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/scripts/register.py"]
CMD ["--workspace", "my_workspace_name", \
     "--run_id", "my_run_id_eg_pipeline_run_id" \
     "--model_uri", "/path/to/my/model.pkl.gz", \
     "--train_uri", "/path/to/my/train_data.csv", \
     "--train_version", "some_has_value", \
     "--score_uri", "/path/to/my/score_data.csv", \
     "--score_version", "some_has_value_for_score", \
     "--params_file", "local_params_file.yml", \
     "--metrics_uri", "/path/to/my/metrics.csv", \
     "--metrics_file", "local_metrics_file.yml"]
