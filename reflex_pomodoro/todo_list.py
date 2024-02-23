"""A component for managing and displaying a list of tasks"""

import json
import uuid

import reflex as rx


class Task(rx.Base):
    key: str
    name: str
    done: bool


class TodoState(rx.State):
    tasks: list[Task]
    active_task_key: str = rx.LocalStorage()
    popover_open: bool = False

    tasks_json: str = rx.LocalStorage()

    def add_task(self, name: str):
        self.tasks.append(Task(key=str(uuid.uuid4()), name=name, done=False))
        self.popover_open = False
        return self.save_tasks()

    def handle_submit(self, form_data: dict[str, str]):
        return self.add_task(form_data["task_name"])

    def _find_task(self, key: str) -> tuple[int, Task | None]:
        for ix, task in enumerate(self.tasks):
            if task.key == key:
                return ix, task
        return -1, None

    def move_task_top(self, key: str):
        ix, task = self._find_task(key)
        if task is not None:
            self.tasks.pop(ix)
            self.tasks.insert(0, task)
            self.active_task_key = task.key
        return self.save_tasks()

    def remove_task(self, key: str):
        ix, task = self._find_task(key)
        if task is not None:
            self.tasks.pop(ix)
        return self.save_tasks()

    def mark_done(self, key: str):
        _, task = self._find_task(key)
        if task:
            task.done = not task.done
            if self.active_task_key == task.key:
                # If the active task is marked as done, clear the active task
                self.active_task_key = ""
        return self.save_tasks()

    def load_tasks(self):
        if self.tasks_json:
            try:
                self.tasks = [Task(**t) for t in json.loads(self.tasks_json)]
            except json.JSONDecodeError:
                self.tasks = []
                self.tasks_json = ""

    def save_tasks(self):
        self.tasks_json = json.dumps([t.dict() for t in self.tasks])


def todo_list_item(task: Task) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.checkbox(
                checked=task.done,
                on_change=lambda checked: TodoState.mark_done(
                    task.key
                ).stop_propagation,
            )
        ),
        rx.table.cell(
            rx.text(
                task.name, text_decoration=rx.cond(task.done, "line-through", "none")
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.icon(
                    "arrow-up-to-line",
                    size=20,
                    on_click=TodoState.move_task_top(task.key).stop_propagation,
                    color="var(--accent-9)",
                    cursor="pointer",
                ),
                rx.icon(
                    "x-square",
                    size=20,
                    on_click=TodoState.remove_task(task.key).stop_propagation,
                    color="var(--accent-9)",
                    cursor="pointer",
                ),
            ),
        ),
        background=rx.cond(
            TodoState.active_task_key == task.key, "var(--accent-3)", "inherit"
        ),
        on_click=TodoState.set_active_task_key(task.key),
    )


def todo_list_table() -> rx.Component:
    return rx.table.root(
        rx.table.body(
            rx.foreach(TodoState.tasks, todo_list_item),
        ),
    )


def todo_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input.root(
                rx.input(placeholder="Add a task", name="task_name"),
                width="100%",
            ),
            rx.icon_button("plus", width="100%"),
        ),
        on_submit=TodoState.handle_submit,
    )


def todo_add_popover() -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.button("Add Task"),
        ),
        rx.popover.content(
            todo_add_form(),
        ),
        open=TodoState.popover_open,
        on_open_change=TodoState.set_popover_open,
    )


def todo_list_component() -> rx.Component:
    return rx.vstack(
        todo_list_table(),
        todo_add_popover(),
        align="center",
    )
