# new idea: use Python's generator yield syntax to return control to our custom Scheduler
# `yield` lets you switch between two functions without weird code or threads
# better idea: instead of abusing `yield` (meant for iteration), let's use Python's async syntax
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
                next(self.current)
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                # this task is finished
                pass


sched = Scheduler()


def countdown(n: int) -> None:
    x = n
    while x >= 0:
        print("down", x)
        time.sleep(1)
        # before yield: step 1
        # after yield: step 2
        # while loop works normally!
        # this is more of an abuse of the `yield` statement
        # generators are meant for iteration, not for function control
        # just this one keyword will confuse many Python programmers!
        yield
        x -= 1


def countup(n: int) -> None:
    x = 0
    while x <= n:
        print("up", x)
        time.sleep(1)
        yield
        x += 1


sched.new_task(countdown(5))
sched.new_task(countup(5))
sched.run()
