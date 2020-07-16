import os
import json
from event_handler.dispatch import BaseDispatchEventHandler


class StartEventHandler(BaseDispatchEventHandler):

    MODEL_START_COMMENT = "Model training has started"
    CHECK_RUN_NAME = "Model Training"
    CHECK_RUN_TITLE = "Model Training Pipeline"
    CHECK_RUN_SUMMARY = "In Progress"
    CHECK_RUN_TEXT = "See details at {}"

    def dispatch(self):
        self.add_comment(self.MODEL_START_COMMENT)
        check_run_text = self.CHECK_RUN_TEXT.format(
            os.getenv("KFP_DSHB")+"/_/pipeline/#/runs")
        self.create_check_run(
            self.CHECK_RUN_NAME, self.CHECK_RUN_TITLE, self.CHECK_RUN_SUMMARY, check_run_text)
