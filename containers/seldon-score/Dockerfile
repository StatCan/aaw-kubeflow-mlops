FROM python:3.7-slim

ENV APP_HOME /app
ENV WORKERS 1
ENV THREADS 8
ENV PORT 8080
WORKDIR $APP_HOME
COPY score.py requirements.txt model.h5 ./

RUN pip install --no-cache-dir -r ./requirements.txt

CMD ["sh","-c","gunicorn --bind 0.0.0.0:$PORT --workers $WORKERS --threads $THREADS score"]
