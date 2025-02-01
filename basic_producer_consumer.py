import queue
import threading
import time


# Queues are great for safe and reliable thread coordination
# Problem: how to do this without threads??
def producer(q, count):
    for n in range(count):
        print("producing", n)
        time.sleep(1)
        q.put(n)
    q.put(None)  # sentinel value indicates end


def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print("consuming", item)
    print("consumer done")


q = queue.Queue()  # thread-safe
threading.Thread(target=producer, args=(q, 10)).start()
threading.Thread(target=consumer, args=(q,)).start()
