import urlparse
import json
import requests


class AppRelease(object):
    @classmethod
    def from_data(cls, data):
        return cls(**data)

    def __init__(self, version, app, commit, env):
        self.version = version
        self.app = app
        self.commit = commit
        self.env = env

    def update_env(self, update):
        self.env.update(update)

    def as_dict(self):
        return dict(version=self.version, app=self.app, commit=self.commit,
                env=self.env)


class AppServiceClient(object):
    def __init__(self, base_uri):
        self._base_uri = base_uri

    def start_new_release(self, app_name, version=0):
        data = dict(version=version)
        json_response = self._post_for_app(app_name, 'start-new-release', data)
        return AppRelease.from_data(json_response)

    def commit_release(self, app_name, release):
        release_dict = release.as_dict()
        return self._post_for_app(app_name, 'commit-release', release_dict)

    def _post_for_app(self, app_name, end_point, obj):
        app_base_url = '/%s/' % app_name
        app_end_point = urlparse.urljoin(app_base_url, end_point)
        return self._post(app_end_point, obj)

    def _post(self, end_point, obj):
        url = urlparse.urljoin(self._base_uri, end_point)
        json_str = json.dumps(obj)
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json_str, headers=headers)
        json_data = response.json
        if not json_data:
            raise Exception('Received no json as a response')
        return json_data
