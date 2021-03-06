import time
import types


# Class for measuring and accumulating time over intervals
class Timer:
    def __init__(self, name):
        self.name = name
        self.start = 0
        self.stop = 0
        self.elapsed = 0

    def go(self):
        self.start = time.time()

    def pause(self):
        self.stop = time.time()
        self.elapsed += self.stop - self.start

    # If self.stop hasn't been set, this function will do it
    def print(self):
        if not self.stop:
            self.pause()
        result = self.elapsed
        unit = "seconds"

        if result < 1:
            unit = "milliseconds"
            result *= 1000
        if result < 1:
            unit = "microseconds"
            result *= 1000
        if result < 1:
            unit = "nanoseconds"
            result *= 1000

        print(unit, " elapsed for segment " + str(self.name) + ": " + str(result))


# Method for measuring execution time
def measure(function, *args):
    assert isinstance(function, types.FunctionType)

    timer = Timer(function.__name__)
    timer.go()
    result = function(*args)
    timer.print()
    return result
