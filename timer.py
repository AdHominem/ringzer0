import time


class Timer:
    def __init__(self, name):
        self.name = name
        self.start = 0
        self.stop = 0

    def start_timer(self):
        self.start = time.time()

    def stop_timer(self):
        self.stop = time.time()

    def print(self):
        print("Milliseconds elapsed for segment " + str(self.name) + ": " + str((self.stop - self.start) * 1000))
