import multiprocessing
import subprocess
import os
from fake_client import dploy_center_test_client
from fake_app_service import dploy_app_service_server

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def start_server():
    server_proc = subprocess.Popen(['dploy-center', '-c',
        os.path.join(CURRENT_DIR, 'conf/dploy.conf')])
    return server_proc


def start_fake_app_service_server():
    app_server_proc = multiprocessing.Process(target=dploy_app_service_server,
                    args=['127.0.0.1', 5558, True])
    app_server_proc.start()
    return app_server_proc


def run_client():
    client_proc = multiprocessing.Process(target=dploy_center_test_client,
            args=['alpha', 'tcp://127.0.0.1:5557', 'tcp://127.0.0.1:5556'])
    try:
        client_proc.start()
        client_proc.join()
    finally:
        client_proc.terminate()


def main():
    # Start server
    server_proc = None
    print "Starting Server"

    try:
        server_proc = start_server()
    except:
        print "Error occured starting the dploy-center server"
        raise

    try:
        app_server_proc = start_fake_app_service_server()
    except:
        print "Error occured starting the AppService server"
        raise

    print "Starting client"
    try:
        run_client()
    finally:
        server_proc.terminate()
        app_server_proc.terminate()


if __name__ == '__main__':
    main()
