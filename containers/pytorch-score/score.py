import time
from io import BytesIO
import datetime
import requests
import numpy as np
from flask import Flask, request
from sklearn.externals import joblib
import nltk


application = Flask(__name__)

model = None
nltk.download('punkt', download_dir='/tmp')


def load_model():
    global model
    if (model is None):
        print('Attempting to load model')
       
        model = joblib.load('/app/model.pkl')
        print('Done loading pipeline!')



@application.route("/predict", methods=['GET', 'POST'])
def run():
    if (request.method == 'GET'):
        return "Healthy"
    else:
        load_model()

        prev_time = time.time()

        post = request.get_json()
        print(post)
        text = post['text']
        print('test input: ',text)
        sentences = process_text(text)
        print('sentences: ', sentences)
        current_time = time.time()

        sent_predictions = model.predict(sentences)
        sent_prediction_scores = model.decision_function(sentences)
        # if any BC found, return 1, else 0.
        doc_prediction = int(sent_predictions.any())

        print('doc_prediction :', doc_prediction)

        inference_time = datetime.timedelta(seconds=current_time - prev_time)


        payload = {
            'time': inference_time.total_seconds(),
            'doc_prediction': doc_prediction
            #'sent_prediction': sent_predictions,
            #'sent_prediction_scores': sent_prediction_scores
        }

        print('Input ({}), Prediction ({})'.format(post['text'], payload))

        return payload


def process_text(doc):

    return nltk.sent_tokenize(doc)



if __name__ == "__main__":
    application.run(host='0.0.0.0')

