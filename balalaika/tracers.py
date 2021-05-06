import re
from weakref import WeakKeyDictionary

import trio
from rich import print as rprint


class BasicTracer(trio.abc.Instrument):
    def __init__(self):
        self.indent = 0

    def before_run(self):
        self._print("!!! run started")
        self.indent += 1

    def _print(self, msg, task=""):
        padding = " " * 4 * self.indent
        rprint(f"{padding}{msg}: {repr(task)}")

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


class MermaidSequenceDiagramTracer(trio.abc.Instrument):
    def __init__(self) -> None:
        self._link = None
        self.out = ""
        self._arrow = "->>"
        self._spaces = "    "
        self._task_name_storage = WeakKeyDictionary()

    def _clean_name(self, task: str) -> str:
        """
        Hacky cleaning to comply with mermaid syntax
        """
        if task in self._task_name_storage:
            return self._task_name_storage[task]
        # we want to map different closures to different names
        uuid = str(id(task)) if "<locals>" in task.name else ""
        clean_name = re.sub(r"[^a-zA-Z0-9\.\_]", "*", task.name) + uuid
        self._task_name_storage[task] = clean_name
        return clean_name

    def _advance_link(self, task):
        task_name = self._clean_name(task)
        if self._link:
            self.out += "\n"
            self.out += f"{self._spaces}{self._link}{self._arrow}{task_name}: "
        self._link = task_name

    def before_task_step(self, task):
        self._advance_link(task)

    def after_run(self):
        out = "sequenceDiagram"
        out += self.out + "."  # not sure why we need this dot
        print(out)
