import os
import json
from kubemlopsbot.gh_actions_client import get_gh_actions_client


class BaseDispatchEventHandler:

    def __init__(self):
        event_payload_file = os.getenv('GITHUB_EVENT_PATH')
        with open(event_payload_file, 'r') as f:
            raw_payload = json.load(f)

            print("Payload")
            print(raw_payload)

            self.event_type = raw_payload['action']
            print(f'::set-output name=EVENT_TYPE::{self.event_type}')

            if ('client_payload' in raw_payload):
                self.event_client_payload = raw_payload['client_payload']

                if ('pr_num' in self.event_client_payload):
                    self.pr_num = self.event_client_payload['pr_num']
                    print(f'::set-output name=ISSUE_NUMBER::{self.pr_num}')
                if ('sha' in self.event_client_payload):
                    self.sha = self.event_client_payload['sha']
                    print(f'::set-output name=SHA::{self.sha}')
                if ('run_id' in self.event_client_payload):
                    self.run_id = self.event_client_payload['run_id']
                    print(f'::set-output name=RUN_ID::{self.run_id}')
            else:
                self.event_client_payload = None

    def add_comment(self, comment):
        if (self.pr_num):
            get_gh_actions_client().add_comment(self.pr_num, comment)

    def add_label(self, label):
        if (self.pr_num):
            get_gh_actions_client().add_labels(self.pr_num, [label])

    def create_check_run(self, name, title, summary, text):
        if (self.sha):
            get_gh_actions_client().create_check_run(self.sha, name, title, summary, text)

    def close_check_run(self, name, conclusion):
        if (self.sha):
            get_gh_actions_client().close_check_run(self.sha, name, conclusion)


    def dispatch(self):
        self.add_comment(self.event_type)
