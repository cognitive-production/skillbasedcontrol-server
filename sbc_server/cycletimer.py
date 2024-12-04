import time
import logging


class CycleTimer:
    def __init__(self, cycletime: float = 1.0, use_cycletime_correction=True):
        """Provides Task to time loops with a cycletime.
        Uses a correction mechanism to compensate calculation time taken by method calls.
        Attention: If you know, that your cycle functionality has highly fluctuating cpu times, dont use cycletime correction (use_cycletime_correction=False)

        Args:
            cycletime (float, optional): target cycletime in seconds. Defaults to 1.0.
            use_cycletime_correction (bool, optional): correction mechanism to compensate calculation time taken by method calls. Defaults to True.
        """
        self.cycletime = cycletime
        self.use_cycletime_correction = use_cycletime_correction
        self.cycletime_correction = 0.0
        self.ts = 0.0
        self.te = 0.0
        self.tec = 0.0
        self.tsleep = 0.0

    def start_cycle(self) -> None:
        """Start cycle."""
        self.ts = time.perf_counter()  # get cycle start time

    def take_time(self) -> float:
        """takes elapsed time since call of startCycle.

        Returns:
            float: elapsed time since call of startCycle.
        """
        return time.perf_counter() - self.ts

    def end_cycle(self, log: bool = False) -> float:
        """End Cycle and wait (time.sleep) remaining time of cycletime.

        Args:
            log (bool, optional): print debug message if cycletime is exceeded (>10%). Defaults to False.

        Returns:
            float: remaining waiting time (time.sleep argument) of cycletime.
        """
        self.te = time.perf_counter()  # get cycle end time
        self.tsleep = (
            self.cycletime - (self.te - self.ts) - self.cycletime_correction
        )  # calculate remaining waiting time including last correction value.
        if self.tsleep > 0.0:  # check is sleep is possible
            time.sleep(self.tsleep)
        if (
            log and self.te - self.ts >= self.cycletime * 1.1
        ):  # print logging warning message
            logging.warning(
                f"CycleTimer exceeded cycletime: Target Cycletime is {self.cycletime}, last cycletime was {self.te-self.ts} with correction {self.cycletime_correction}"
            )
        if self.use_cycletime_correction:
            self.tec = (
                time.perf_counter()
            )  # get cycle end time for correction, including sleep time
            self.cycletime_correction = max(
                self.tec - self.ts - self.cycletime, 0.0
            )  # calculate correction time for next cycle
        return self.tsleep


if __name__ == "__main__":
    # Usage example with debug information
    import random

    cycletime = 0.02
    loops = 10
    ts0 = 0.0
    te0 = 0.0
    dsleeptimes: list = [0.0] * loops

    cycleTimer = CycleTimer(cycletime=cycletime)
    ts0 = time.perf_counter()

    for i in range(loops):
        cycleTimer.start_cycle()
        time.sleep(cycletime / (2.0 + random.random() * 5.0))
        cycleTimer.end_cycle()
        dsleeptimes[i] = cycleTimer.cycletime_correction

    te0 = time.perf_counter()
    dsleeptimes = [dsleeptime * 1e3 for dsleeptime in dsleeptimes]
    print(f"Time waited: ")
    print(f"Overall: {1E3*(((te0-ts0)/loops)-cycletime)} ms")
    print(f"Mean: {sum(dsleeptimes)/len(dsleeptimes)} ms")
    print(f"Min: {min(dsleeptimes)} ms at {dsleeptimes.index(min(dsleeptimes))}")
    print(f"Max: {max(dsleeptimes)} ms at {dsleeptimes.index(max(dsleeptimes))}")
