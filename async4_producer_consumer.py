import heapq
import queue
import threading
import time
from collections import deque


class Scheduler3:
    # **unchanged** async3 Scheduler!
    # how will we use the async3 Scheduler to not use threads and share data between functions?
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


class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # all getters waiting for data

    def put(self, item):
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            # do we call getter right away here?
            # func(item)
            # or do we schedule it to call later?
            # it's best to schedule it in case the getter is slow/nested/complicated
            sched.call_soon(func)

    def get(self, callback):
        ### how to wait until an item is ready?
        # very weird
        # one way is to pass a callback to get()
        # callback is called once the item is ready
        if self.items:
            callback(self.items.popleft())
        else:
            # if no data available, then put the getter into a list and call it eventually
            self.waiting.append(lambda: self.get(callback))


# Queues are great for safe and reliable thread coordination
# Problem: how to do this without threads??
def producer(q, count):
    # no more for loops!
    # no time.sleep!
    def _run(n):
        if n < count:
            print("producing", n)
            q.put(n)
            sched.call_later(1, lambda: _run(n + 1))
        else:
            print("producer done")
            q.put(None)

    _run(0)


def consumer(q):
    def _consume(item):
        # called only when item is available
        if item is None:
            print("consumer done")
        else:
            print("consuming", item)
            sched.call_soon(lambda: consumer(q))

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 10))
sched.call_soon(lambda: consumer(q))
sched.run()
