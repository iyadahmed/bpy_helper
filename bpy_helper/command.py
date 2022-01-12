from collections import deque
from typing import Callable, Deque


class Command:
    def __init__(self, function: Callable, *args, **kwargs):
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def execute(self):
        self._function(*self._args, **self._kwargs)


class CommandQueue:
    def __init__(self) -> None:
        self.queue: Deque[Command] = deque()
        self._num_added_commands = 0

    def append(self, cmd: Command):
        self.queue.append(cmd)
        self._num_added_commands += 1

    def execute_next(self):
        cmd = self.queue.popleft()
        cmd.execute()

    def get_progress(self):
        """Value in range 0. to 1. indicating progress"""
        if self._num_added_commands == 0:
            return 1.0
        return 1 - (len(self.queue) / self._num_added_commands)

    def is_finished(self):
        return len(self.queue) == 0
