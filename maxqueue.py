from collections import deque

class MaxSizeQueue:
    def __init__(self, max_size):
        self.queue = deque(maxlen=max_size)

    def enqueue(self, item):
        self.queue.append(item)

    def dequeue(self):
        if len(self.queue) > 0:
            return self.queue.popleft()
        else:
            raise IndexError("Queue is empty")

    def size(self):
        return len(self.queue)

    def is_empty(self):
        return len(self.queue) == 0

    def is_full(self):
        return len(self.queue) == self.queue.maxlen

    def __str__(self):
        return str(list(self.queue))
    
    def get_list(self):
        return list(self.queue)