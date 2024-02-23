import reflex as rx

from .settings import SettingsState, settings_dialog
from .timer import TimerState, timer


class State(SettingsState):
    """The app state."""

    n_breaks: int = 0
    completed_works: int = 0
    is_work: bool = False

    def start_new_cycle(self, skip: bool = False):
        if not skip:
            if self.is_work:
                self.completed_works += 1
        if not self.is_work:
            self.n_breaks += 1

        self.is_work = not self.is_work
        return TimerState.reset_to(
            self.work_time_m * 60
            if self.is_work
            else (
                self.long_break_time_m * 60
                if self.n_breaks % self.long_break_interval == 0
                else self.break_time_m * 60
            )
        )


def index() -> rx.Component:
    return rx.vstack(
        # rx.theme_panel(),
        timer(height="200px", width="200px"),
        rx.hstack(
            rx.cond(
                TimerState.is_done,
                rx.button(
                    "Next",
                    on_click=State.start_new_cycle(False),
                ),
                rx.button(
                    "Skip",
                    on_click=State.start_new_cycle(True),
                ),
            ),
            settings_dialog(),
        ),
        align="center",
    )


app = rx.App()
app.add_page(index, on_load=SettingsState.load_settings)
