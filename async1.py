import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # functions to execute

    def call_soon(self, func):
        self.ready.append(func)

    def run(self):
        while self.ready:
            func = self.ready.popleft()
            func()


# Very strange code, all async scheduling internals visible
sched = Scheduler()


def countdown(n):
    if n >= 0:
        print("down", n)
        time.sleep(1)
        # jump back into scheduler "await"
        sched.call_soon(lambda: countdown(n - 1))


def countup(stop, x=0):
    # x - Internal state must be stored throughout the function calls to countup()
    # Option 1: use a default argument
    if x <= stop:
        print("up", x)
        time.sleep(1)
        sched.call_soon(lambda: countup(stop, x=x + 1))


def countup2(stop):
    # x - Internal state must be stored throughout the function calls to countup()
    # Option 2: use a nested function (a closure)
    def _run(x):
        if x <= stop:
            print("up", x)
            time.sleep(1)
            sched.call_soon(lambda: _run(x + 1))

    _run(0)


sched.call_soon(lambda: countdown(3))
# sched.call_soon(lambda: countup(3))
sched.call_soon(lambda: countup2(3))
sched.run()
