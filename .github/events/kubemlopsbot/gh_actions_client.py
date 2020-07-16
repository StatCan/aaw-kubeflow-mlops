import os
import requests


class GhActionsClient:

    def __init__(self, repo, pat):
        self.owner, self.repo = repo.split("/")
        self.personal_access_token = pat

        self.base_url = f'https://api.github.com/repos/{self.owner}/{self.repo}'  # noqa: E501
        self.headers = {'authorization': f'token {self.personal_access_token}',
                        'accept': 'application/vnd.github.antiope-preview+json'}  # noqa: E501

    def send_dispatch_event(self, event_type, client_payload):
        url = self.base_url + "/dispatches"
        data = {'event_type': event_type, 'client_payload': client_payload}
        response = requests.post(url=url, headers=self.headers, json=data)
        print(response.content)
        assert response.status_code == 204

    def add_comment(self, pr_num, comment):
        url = self.base_url + "/issues/{pr_num}/comments".format(pr_num=pr_num)
        data = {'body': comment}
        response = requests.post(url=url, headers=self.headers, json=data)
        print(response.content)
        assert response.status_code == 201

    def add_labels(self, pr_num, labels):
        url = self.base_url + "/issues/{pr_num}/labels".format(pr_num=pr_num)
        data = {'labels': labels}
        response = requests.post(url=url, headers=self.headers, json=data)
        assert response.status_code == 200
        print(response.content)

    def create_check_run(self, sha, name, title, summary, text):
        url = self.base_url + "/check-runs"
        data = {
            'name': f'{name}',
            'head_sha': f'{sha}',
            'status': 'in_progress',
            'output': {
                'title': f'{title}',
                'summary': f'{summary}',
                'text': f'{text}'
            },
        }
        print(data)
        response = requests.post(url=url, headers=self.headers, json=data)
        print(response.content)
        assert response.status_code == 201

    def close_check_run(self, sha, name, conclustion):
        url = self.base_url + "/check-runs"
        data = {
            'name': f'{name}',
            'conclusion': f'{conclustion}',
            'head_sha': f'{sha}'
        }
        print(data)
        response = requests.post(url=url, headers=self.headers, json=data)
        print(response.content)
        assert response.status_code == 201


def get_gh_actions_client():
    return GhActionsClient(os.getenv("GITHUB_REPOSITORY"),
                           os.getenv("GITHUB_TOKEN"))
