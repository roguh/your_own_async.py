# better idea: instead of abusing `yield` (meant for iteration), let's use Python's async syntax
# all of Python's syntax can be leveraged through magic methods like __await__()
# async/await syntax added to Python 3.5 many years ago
#
# we now have a custom Python async scheduler implemented with Python Python generators!
import time
import heapq
from collections import deque


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


# problem with __await__: it can only appear within a function declared to be `async`
async def countdown(n: int) -> None:
    x = n
    while x >= 0:
        print("down", x)
        # Just like normal async code and very similar to the basic code!
        await sched.sleep(4)
        x -= 1


async def countup(n: int) -> None:
    x = 0
    while x <= n:
        print("up", x)
        await sched.sleep(1)
        x += 1


sched.new_task(countdown(3))
sched.new_task(countup(12))
sched.run()
