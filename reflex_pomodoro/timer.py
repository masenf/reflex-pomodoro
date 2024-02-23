"""The high level Timer component of the app."""
import datetime

import reflex as rx

from .components.react_circular_progress import circular_progressbar_with_children


class TimerState(rx.State):
    total_time_s: int
    time_elapsed_s: float = 0.0
    tick_interval_ms: int = 1000

    def tick(self, _date):
        if not self.is_done:
            self.time_elapsed_s = self.time_elapsed_s + (self.tick_interval_ms / 1000)
        else:
            self.tick_interval_ms = 0

    def reset_to(self, time_s: int):
        self.total_time_s = time_s
        self.time_elapsed_s = 0.0
        self.tick_interval_ms = 1000

    def toggle_running(self):
        if self.tick_interval_ms == 0:
            self.tick_interval_ms = 1000
        else:
            self.tick_interval_ms = 0

    @rx.cached_var
    def time_elapsed_fmt(self) -> str:
        return str(
            datetime.timedelta(seconds=self.total_time_s - self.time_elapsed_s)
        ).partition(":")[2]

    @rx.cached_var
    def is_running(self) -> bool:
        return self.tick_interval_ms > 0

    @rx.cached_var
    def is_done(self) -> bool:
        return self.time_elapsed_s >= self.total_time_s


def timer(**box_props) -> rx.Component:
    color_props = {
        "color": "var(--accent-10)",
    }
    return rx.box(
        rx.moment(interval=TimerState.tick_interval_ms, on_change=TimerState.tick, display="none"),
        circular_progressbar_with_children(
            rx.vstack(
                rx.heading(TimerState.time_elapsed_fmt, **color_props),
                rx.cond(
                    TimerState.is_running,
                    rx.icon("pause", **color_props),
                    rx.icon("play", **color_props),
                ),
                align="center",
            ),
            value=TimerState.time_elapsed_s,
            max_value=TimerState.total_time_s,
        ),
        on_click=TimerState.toggle_running,
        **box_props,
    )
