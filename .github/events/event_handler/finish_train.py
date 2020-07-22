import os
import json
from event_handler.dispatch import BaseDispatchEventHandler


class FinishEventHandler(BaseDispatchEventHandler):

    MODEL_FINISH_COMMENT = "Model training has finished"
    CHECK_RUN_NAME = "Model Training"

    def __init__(self):
        super().__init__()
        if (self.event_client_payload):
            if ('status' in self.event_client_payload):
                self.status = self.event_client_payload['status']
                print(f'::set-output name=STATUS::{self.status}')

    def dispatch(self):
        self.add_comment(self.MODEL_FINISH_COMMENT)
        if (self.status == 'Succeeded'):
            conclusion = "success"
        else:
            conclusion = "failure"
        self.close_check_run(self.CHECK_RUN_NAME, conclusion)
