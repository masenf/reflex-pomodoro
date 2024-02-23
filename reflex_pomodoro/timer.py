"""The high level Timer component of the app."""

import reflex as rx

from . import sfx
from .components.react_circular_progress import circular_progressbar_with_children
from .components.tickler import tickler
from .components.use_state import integral_fragment


class TimerState(rx.State):
    total_time_s: int
    time_elapsed_s: float = 0.0
    tick_interval_ms: int = 0
    reset_timer: bool = False
    is_work: bool = True

    def reset_to(self, time_s: int, start: bool, is_work: bool):
        self.total_time_s = time_s
        self.time_elapsed_s = 0.0
        self.tick_interval_ms = 1000 if start else 0
        self.is_work = is_work
        self.reset_timer = True

    def toggle_running(self):
        if self.tick_interval_ms == 0:
            self.tick_interval_ms = 1000
        else:
            self.tick_interval_ms = 0

    def on_tick_limit(self, n_ticks):
        self.tick_interval_ms = 0
        self.time_elapsed_s = n_ticks
        if self.is_work:
            return sfx.work_done_sfx()
        else:
            return sfx.break_done_sfx()

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
    ticks = tickler(
        interval=TimerState.tick_interval_ms,
        tick_limit=TimerState.total_time_s,
        tick_should_reset=TimerState.reset_timer,
        on_reset=TimerState.set_reset_timer(False),
        on_tick_limit=TimerState.on_tick_limit,
    )
    timer = rx.box(
        circular_progressbar_with_children(
            rx.vstack(
                rx.heading(
                    rx.moment(
                        date=(TimerState.total_time_s - ticks.value + 0.1).to(str),
                        unix=True,
                        format="mm:ss",
                    ),
                    **color_props,
                ),
                rx.cond(
                    TimerState.is_running,
                    rx.icon("pause", **color_props),
                    rx.icon("play", **color_props),
                ),
                align="center",
            ),
            value=ticks.value,
            max_value=TimerState.total_time_s,
        ),
        on_click=TimerState.toggle_running,
        **box_props,
    )
    return integral_fragment(timer, ticks)
