import os
import threading
import time


def countdown(n: int) -> None:
    x = n
    while x >= 0:
        print("down", x)
        time.sleep(1)
        x -= 1


def countup(n: int) -> None:
    x = 0
    while x <= n:
        print("up", x)
        time.sleep(1)
        x += 1


THREADED = bool(os.getenv("THREADED"))
if THREADED:
    threading.Thread(target=lambda: countdown(3)).start()
    threading.Thread(target=lambda: countup(3)).start()
else:
    countdown(3)
    countup(3)
