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




class bert_predictor():
    
    def __init__(self, path):
        
        # Load BertForSequenceClassification, the pretrained BERT model with a single 
        # linear classification layer on top. 
        self.model = BertForSequenceClassification.from_pretrained(
            path, #"bert-base-uncased", # Use the 12-layer BERT model, with an uncased vocab.
            num_labels = 2, # The number of output labels--2 for binary classification.
                            # You can increase this for multi-class tasks.   
            output_attentions = False, # Whether the model returns attentions weights.
            output_hidden_states = False, # Whether the model returns all hidden-states.
        )
        
        # Load the BERT tokenizer.
        print('Loading BERT tokenizer...')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        print('vocab size ',self.tokenizer.vocab_size)

    def predict(self, sentences):
        
        input_ids, attention_masks = self.tokenize(sentences)
        input_ids = torch.tensor(input_ids)
        attention_masks = torch.tensor(attention_masks)

        
        # Telling the model not to compute or store gradients, saving memory and 
        # speeding up prediction
        with torch.no_grad():
            # Forward pass, calculate logit predictions
            outputs = self.model(input_ids, token_type_ids=None, 
                          attention_mask=attention_masks)
            logits = outputs[0]
            # Move logits and labels to CPU
            probs = torch.softmax(logits,dim=1).detach().cpu().numpy()

        probs = [float(prob[1]) for prob in probs]
        return probs

    
    def tokenize(self, sentences):

        MAX_LEN = 128

        # Tokenize all of the sentences and map the tokens to thier word IDs.
        input_ids = []
        attention_masks = []

        # For every sentence...
        for sent in sentences:
            # `encode` will:
            #   (1) Tokenize the sentence.
            #   (2) Prepend the `[CLS]` token to the start.
            #   (3) Append the `[SEP]` token to the end.
            #   (4) Map tokens to their IDs.
            encoded_sent = self.tokenizer.encode_plus(
                text=sent,  # Preprocess sentence
                add_special_tokens=True,        # Add `[CLS]` and `[SEP]`
                max_length=MAX_LEN,                  # Max length to truncate/pad
                pad_to_max_length=True,         # Pad sentence to max length
                return_attention_mask=True,     # Return attention mask
                truncation=True # explicitly trunace longer sentences to MAX_LEN
                )

            # Add the encoded sentence to the list.
            input_ids.append(encoded_sent['input_ids'])
            attention_masks.append(encoded_sent['attention_mask'])

        input_ids = np.array(input_ids)
        # Print sentence 0, now as a list of IDs.
        print('Original: ', sentences[0])
        print('Token IDs:', input_ids[0])
        print('attention Masks:', attention_masks[0])

        return input_ids, attention_masks


def load_model():
    global model
    if (model is None):
        print('Attempting to load model')
        model = bert_predictor('/app')
        print('Done loading pytorch model!')



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

        sent_prediction_scores = model.predict(sentences)
        # 0/1 prediction for threshold 0.5
        sent_predictions = 1*np.array(np.array(sent_prediction_scores) > 0.5)
        
        # if any BC found, return 1, else 0.
        doc_prediction = int(sent_predictions.any())

        print('doc_prediction :', doc_prediction)

        inference_time = datetime.timedelta(seconds=current_time - prev_time)

        sent_predictions = [int(el) for el in list(sent_predictions)]
        sent_prediction_scores = [float(el) for el in list(sent_prediction_scores)]

        payload = {
            'time': inference_time.total_seconds(),
            'doc_prediction': doc_prediction,
            'sent_prediction': sent_predictions,
            'sent_prediction_scores': sent_prediction_scores
        }

        print('Input ({}), Prediction ({})'.format(post['text'], payload))

        return payload



def process_text(doc):

    return nltk.sent_tokenize(doc)


if __name__ == "__main__":
    application.run(host='0.0.0.0')

