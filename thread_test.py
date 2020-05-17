from queue import Queue
from threading import Thread
from agents.helpers.graph import Graph
import threading
import time


class Agent(Thread):
    def __init__(self, queue, user):
        super().__init__(name=user)
        self.queue = queue

    def run(self):
        q = self.queue
        while True:
            print(q.get())
            q.task_done()
            time.sleep(3)

def do_stuff(q):
    while True:
        q.get()
        q.task_done()

queue = Queue(maxsize=0)
n_threads = 2

t1 = Agent(queue, user=f'Bubbels {1}')
t1.setDaemon(True)
t1.start()

t2 = Agent(queue, user=f'Bubbels {2}')
t2.setDaemon(True)
t2.start()



for x in range(10):
    queue.put(x)
