import trio
from rich import print


class BasicTracer(trio.abc.Instrument):
    def __init__(self):
        self.indent = 0

    def before_run(self):
        self._print("!!! run started")
        self.indent += 1

    def _print(self, msg, task=""):
        padding = " " * 4 * self.indent
        print(f"{padding}{msg}: {task}")

    def task_spawned(self, task):
        self._print("### new task spawned", task)

    def task_scheduled(self, task):
        self._print("### task scheduled", task)

    def before_task_step(self, task):
        self._print(">>> about to run one step of task", task)
        self.indent += 1

    def after_task_step(self, task):
        self.indent -= 1
        self._print("<<< task step finished", task)

    def task_exited(self, task):
        self._print("### task exited", task)

    def before_io_wait(self, timeout):
        if timeout:
            self._print(f"### waiting for I/O for up to {timeout} seconds")
        else:
            self._print("### doing a quick check for I/O")
        self._sleep_time = trio.current_time()

    def after_io_wait(self, timeout):
        duration = trio.current_time() - self._sleep_time
        self._print(f"### finished I/O check (took {duration} seconds)")

    def after_run(self):
        self.indent -= 1
        self._print("!!! run finished")
