import os
import json
from event_handler.dispatch import BaseDispatchEventHandler


class RegModelEventHandler(BaseDispatchEventHandler):

    MODEL_REGISTRATION_COMMENT = "Model **{model_name}** has been registered \
                                  at the [Model Registry ](http://microsoft.com) \
                                  with the following metrics **{metrics}**"
    MODEL_REGISTRATION_LABEL = "Model Registered"


    # TODO: Fetch params from MLFlow
    def get_model_params(self):
        return {'model_name': 'Mexican Food',
                'metrics': 'Spicy level:10.0'}


    def dispatch(self):
        model_params = self.get_model_params()
        comment = self.MODEL_REGISTRATION_COMMENT.format(model_name=model_params['model_name'],
                                                  metrics=model_params['metrics'])
        self.add_comment(comment)
        self.add_label(self.MODEL_REGISTRATION_LABEL)
