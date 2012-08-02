from mock import ANY


def msg(msg_type, msg_sub_type, message=None):
    return {
        'type': msg_type,
        'message': {
            'type': msg_sub_type,
            'data': message,
        }
    }


_ALPHA_REQUEST = {
    "broadcast_id": "12345abcdef:12345",
    "app": "alpha",
    "archive_uri": "somepath.tar.gz",
    "commit": "12345",
    "update_message": "message",
    "metadata_version": 0
}
_ALPHA_EXPECTED = [
    msg('output', 'line', 'Retrieving App metadata for "alpha"'),
    msg('output', 'line', 'Initializing cargo build for "alpha"'),
    msg('output', 'line', 'Cargo build for "alpha" completed!'),
    msg('output', 'line', 'Stopping any active deployments for "alpha"'),
    msg('output', 'line', 'Deploying cargo to 2 zones'),
    msg('output', 'line', 'Deployment completed')
]


CLIENT_FIXTURES = {
    "__common__": [
        msg('status', 'completed'),
    ],
    "alpha": [
        _ALPHA_REQUEST,
        _ALPHA_EXPECTED
    ]
}


def build_and_deploy_data(release, app, commit, env):
    data = {
        "release_version": release,
        "app": app,
        "commit": commit,
        "env": env,
    }
    return data


APP_SERVICE_FIXTURES = {
    "alpha": {
        "new-build-and-deploy-data": [
            # Input
            ANY,
            # Output
            build_and_deploy_data(10, "alpha", "12345",
                dict(MYSQL_NAME="name")),
        ],
        "commit-new-build-data": [
            # Input
            ANY,
            # Output
            {'status': "ok"},
        ]
    }
}
