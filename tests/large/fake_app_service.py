from fixtures import APP_SERVICE_FIXTURES
from flask import Flask, jsonify


app = Flask(__name__)


def get_current_fixture_data(app_name, route):
    app_fixtures = APP_SERVICE_FIXTURES.get(app_name)
    return app_fixtures.get(route)


@app.route('/<app_name>/start-new-release', methods=['POST'])
def start_new_release(app_name):
    fixture = get_current_fixture_data(app_name, 'start-new-release')
    return jsonify(fixture)


@app.route('/<app_name>/commit-release', methods=['POST'])
def commit_release(app_name):
    """Commit the current release upon success"""
    fixture = get_current_fixture_data(app_name, 'commit-release')
    return jsonify(fixture)


@app.route('/<app_name>/rollback-release', methods=['POST'])
def rollback_release(app_name):
    """Rollback the current release because there was an error"""
    fixture = get_current_fixture_data(app_name, 'rollback-release')
    return jsonify(fixture)


def dploy_app_service_server(host, port, debug=True):
    app.run(host=host, port=port, debug=debug, use_reloader=False)
