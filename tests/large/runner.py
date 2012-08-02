import multiprocessing
import subprocess
import time
from fake_client import dploy_center_test_client


def start_server():
    server_proc = subprocess.Popen(['dploy-center', '-c',
        'conf/dploy.conf'])
    return server_proc


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
        print "Error occured starting the server"
        raise
    print "Starting client"
    try:
        run_client()
    finally:
        server_proc.terminate()


if __name__ == '__main__':
    main()
