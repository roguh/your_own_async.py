# changes: use Python's efficient heapq priority queue to implement Scheduler.call_later
#
# time.sleep has problems when you run it from a non-trivial async program
# time.sleep blocks EVERYTHING, so we need a custom time.sleep that works with our scheduler
# example: what if we wanted async1 but with different delays of time.sleep(4) and time.sleep(2)
from collections import deque
import heapq
import time


class Scheduler3:
    def __init__(self):
        self.ready = deque()  # functions to execute
        self.sleeping = []
        self.sequence = 0  # tie-break functions with same deadline

    def call_soon(self, func):
        self.ready.append(func)

    def call_later(self, delay: float, func):
        # All async frameworks need a way to delay function calls

        self.sequence += 1
        deadline = time.time() + delay
        # heap implementation of a priority queue
        # much more efficient than sorting a list every time
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

        # POTENTIAL BUG: what if both functions have exactly the same deadline?
        ## heapq.heappush(self.sleeping, (deadline, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # sleep until nearest deadline
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()


# Very strange code, all async scheduling internals visible
sched = Scheduler3()


def countdown(n):
    if n >= 0:
        print("down", n)
        # time.sleep(4)
        sched.call_later(4, lambda: countdown(n - 1))


def countup2(stop):
    # x - Internal state must be stored throughout the function calls to countup()
    # Option 2: use a nested function (a closure)
    def _run(x):
        if x <= stop:
            print("up", x)
            # time.sleep(1)
            sched.call_later(1, lambda: _run(x + 1))

    _run(0)


sched.call_soon(lambda: countdown(3))
sched.call_soon(lambda: countup2(3))
sched.run()
