# better idea: instead of abusing `yield` (meant for iteration), let's use Python's async syntax
# all of Python's syntax can be leveraged through magic methods like __await__()
# async/await syntax added to Python 3.5 many years ago
#
# we now have a custom Python async scheduler implemented with Python Python generators!
import time
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.current = None

    def new_task(self, gen):
        self.ready.append(gen)

    def run(self):
        while self.ready:
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


sched = Scheduler()


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
        time.sleep(1)
        # before yield: step 1
        # after yield: step 2
        # while loop works normally!
        await switch()
        x -= 1


async def countup(n: int) -> None:
    x = 0
    while x <= n:
        print("up", x)
        time.sleep(1)
        await switch()
        x += 1


sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()
