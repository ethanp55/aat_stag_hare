import time

class Timer:
    def __init__(self, time_limit: float = 60):
        self.start = time.time()
        self.time_limit = time_limit

    def time(self) -> float:
        return time.time() - self.start

    def time_out(self) -> bool:
        return self.time() > self.time_limit