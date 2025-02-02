# better idea: instead of abusing `yield` (meant for iteration), let's use Python's async syntax
# all of Python's syntax can be leveraged through magic methods like __await__()
# async/await syntax added to Python 3.5 many years ago
#
# we now have a custom Python async scheduler implemented with Python Python generators!
import heapq
import time
from collections import deque

# -------------- same Scheduler8 code as in async 8


class Scheduler8:
    def __init__(self):
        self.ready = deque()
        self.current = None
        self.sleeping = []
        self.sequence = 0

    def new_task(self, coro):
        self.ready.append(coro)

    async def sleep(self, delay):
        # the current task wants to sleep, but how?
        deadline = time.time() + delay
        self.sequence += 1
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None  # disappear
        await switch()  # go to next task

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, coro = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(coro)
            # run next task, which is a generator
            self.current = self.ready.popleft()
            try:
                # send None to async function
                # an async function is a Coroutine and we can "activate" it with .send()
                self.current.send(None)
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                # this task is finished
                pass


sched = Scheduler8()


class Awaitable:
    # goal: let's hide the `yield` staatement` with Python's await syntax
    def __await__(self):
        # this is more of an abuse of the `yield` statement
        # generators are meant for iteration, not for function control
        # just this one keyword will confuse many Python programmers!
        yield


def switch():
    return Awaitable()


# -------------- same Scheduler8 code as in async 8


class QueueClosed(Exception):
    pass
class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()
        self._closed = False
    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            # what if len(self.items)>0?
            sched.ready.append(self.waiting.popleft())

    def put(self, item):
        if self._closed:
            raise QueueClosed()
        self.items.append(item)
        if self.waiting:
            sched.ready.append(self.waiting.popleft())

    async def get(self):
        while not self.items:
            if self._closed:
                # no need for messy callback hell and custom Result class!
                raise QueueClosed()
            # sleep
            self.waiting.append(sched.current)
            # disappear from the scene for now
            sched.current = None
            # switch to another task
            await switch()
        return self.items.popleft()


async def producer(q, count):
    for n in range(count):
        print("producing", n)
        q.put(n)
        await sched.sleep(1)
    print("producer done")
    q.close()


async def consumer(q):
    try:
        while True:
            item = await q.get()
            print("consuming", item)
    except QueueClosed:
        print("consumer done")


q = AsyncQueue()
sched.new_task(producer(q, 3))
sched.new_task(consumer(q))
sched.run()
