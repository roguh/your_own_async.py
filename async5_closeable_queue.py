# async4 and async5 problem: callback hell! difficult to understand. let's use Python generators next (yield)
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


class QueueClosed(Exception):
    pass


class Result:
    def __init__(self, value=None, exc=None):
        self.value = value
        self.exc = exc

    def result(self):
        if self.exc:
            raise self.exc
        else:
            return self.value


class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # all getters waiting for data
        self._closed = False

    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            # let getters know of close
            for func in self.waiting:
                sched.call_soon(func)

    def put(self, item):
        if self._closed:
            raise QueueClosed()
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            # do we call getter right away here?
            # func(item)
            # or do we schedule it to call later?
            # it's best to schedule it in case the getter is slow/nested/complicated
            sched.call_soon(func)

    def get(self, callback):
        # you can call get() until the queue is empty even if the queue is closed

        ### how to wait until an item is ready?
        # very weird
        # one way is to pass a callback to get()
        # callback is called once the item is ready
        if self.items:
            # return a good result
            callback(Result(value=self.items.popleft()))
        else:
            if self._closed:
                # raise exception
                callback(Result(exc=QueueClosed()))
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
            q.close()  # no more items, no need for the None hack

    _run(0)


def consumer(q):
    def _consume(result):
        try:
            item = result.result()
            # called only when item is available
            print("consuming", item)
            sched.call_soon(lambda: consumer(q))
        except QueueClosed:
            print("consumer done")

    q.get(callback=_consume)


q = AsyncQueue()
sched.call_soon(lambda: producer(q, 3))
sched.call_soon(lambda: consumer(q))
sched.run()
