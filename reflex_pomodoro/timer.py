"""The high level Timer component of the app."""
import reflex as rx

from .components.react_circular_progress import circular_progressbar_with_children
from .use_state import IntegralFragment, useState


class TimerState(rx.State):
    total_time_s: int
    time_elapsed_s: float = 0.0
    tick_interval_ms: int = 0
    reset_timer: bool = False

    def reset_to(self, time_s: int, start: bool = False):
        self.total_time_s = time_s
        self.time_elapsed_s = 0.0
        self.tick_interval_ms = 1000 if start else 0 
        self.reset_timer = True

    def toggle_running(self):
        if self.tick_interval_ms == 0:
            self.tick_interval_ms = 1000
        else:
            self.tick_interval_ms = 0

    @rx.cached_var
    def is_running(self) -> bool:
        return self.tick_interval_ms > 0

    @rx.cached_var
    def is_done(self) -> bool:
        return self.time_elapsed_s >= self.total_time_s


class LocalTickState:
    """Keep track of the number of ticks that have occurred locally.
    
    Update the backend TimerState when the limit is reached.
    """
    value, set_value = useState("localTimeElapsedS", 0.001)

    _value_name = value._var_name_unwrapped
    _tick_limit = TimerState.total_time_s._var_name_unwrapped
    _reset_timer = TimerState.reset_timer._var_name_unwrapped

    @classmethod
    def _stop_timer_backend(cls) -> str:
        return rx.utils.format.format_event_chain(
            rx.EventChain(
                events=[
                    TimerState.set_tick_interval_ms(0),
                    TimerState.set_time_elapsed_s(cls.value),
                ],
            )
        )

    @classmethod
    def on_tick(cls) -> rx.Var:
        return rx.Var.create(
            "e => {"
                f"if({cls._value_name} < {cls._tick_limit})"
                "{" +
                    # Update the frontend state to show timer progress.
                    f"{cls.set_value}({cls._value_name} + 1)"
                + "} else {"
                    # Update the backend state to mark timer as stopped.
                    f"{cls._stop_timer_backend()}"
                "}"
            "}",
        )._replace(
            _var_type=rx.EventChain,
            merge_var_data=cls.value._var_data,
        )

    @classmethod
    def _reset_backend(cls) -> str:
        return rx.utils.format.format_event_chain(
            rx.EventChain(
                events=[
                    TimerState.set_reset_timer(False),
                ],
            )
        )

    @classmethod
    def on_reset_requested(cls) -> rx.Var:
        return rx.Var.create(
            "e => {"
                f"{cls.set_value}(0.001); {cls._reset_backend()};"
            "}"
        )._replace(
            _var_type=rx.EventChain,
            merge_var_data=cls.value._var_data,
        )


def timer(**box_props) -> rx.Component:
    color_props = {
        "color": "var(--accent-10)",
    }
    timer = rx.box(
        circular_progressbar_with_children(
            rx.vstack(
                rx.heading(
                    rx.moment(
                        date=(TimerState.total_time_s - LocalTickState.value + 1).to(str),
                        unix=True,
                        format="mm:ss",
                        interval=TimerState.tick_interval_ms,
                        on_change=LocalTickState.on_tick(),
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
            value=LocalTickState.value,
            max_value=TimerState.total_time_s,
        ),
        on_click=TimerState.toggle_running,
        **box_props,
    )
    return IntegralFragment.create(
        timer,
        # Apply reset to local tick state when the backend state requests it.
        rx.cond(
            TimerState.reset_timer,
            rx.moment(
                interval=20,
                on_change=LocalTickState.on_reset_requested(),
            ),
        ),
    )
