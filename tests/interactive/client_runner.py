import multiprocessing
import sys
from fake_client import send_random_request


def main():
    processes = []
    for i in range(int(sys.argv[2])):
        process = multiprocessing.Process(target=send_random_request,
                args=(sys.argv[1],))
        process.start()

    while True:
        quit = True
        for process in processes:
            if process.is_alive():
                quit = False
                process.join()
        if quit:
            break


if __name__ == '__main__':
    main()
