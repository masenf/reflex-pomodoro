"""The high level Timer component of the app."""
import datetime

import reflex as rx
from reflex.components.component import MemoizationLeaf

from .components.react_circular_progress import circular_progressbar_with_children


LOCAL_TIME_ELAPSED_S_VALUE = "local_time_elapsed_s"
SET_LOCAL_TIME_ELAPSED_S_VALUE = "set_local_time_elapsed_s_value"
LOCAL_TIME_ELAPSED_S_VAR_DATA = rx.vars.VarData(
    imports={"react": {rx.utils.imports.ImportVar(tag="useState")}},
    hooks={f"const [{LOCAL_TIME_ELAPSED_S_VALUE}, {SET_LOCAL_TIME_ELAPSED_S_VALUE}] = useState(0.001);"},
)
LOCAL_TIME_ELAPSED_S_VAR = rx.Var.create(LOCAL_TIME_ELAPSED_S_VALUE)._replace(
    _var_type=float,
    _var_is_local=False,
    _var_is_string=False,
    merge_var_data=LOCAL_TIME_ELAPSED_S_VAR_DATA,
)


class IntegralFragment(rx.Fragment, MemoizationLeaf):
    pass


class TimerState(rx.State):
    total_time_s: int
    time_elapsed_s: float = 0.0
    tick_interval_ms: int = 0
    reset_timer: bool = False

    def reset_to(self, time_s: int):
        # self.total_time_s = time_s
        self.total_time_s = 10
        self.time_elapsed_s = 0.0
        self.tick_interval_ms = 1000
        self.reset_timer = True

    def toggle_running(self):
        if self.tick_interval_ms == 0:
            if self.reset_timer:
                self.reset_timer = False
            self.tick_interval_ms = 1000
        else:
            self.tick_interval_ms = 0

    @rx.cached_var
    def is_running(self) -> bool:
        return self.tick_interval_ms > 0

    @rx.cached_var
    def is_done(self) -> bool:
        return self.time_elapsed_s >= self.total_time_s


LOCAL_TIME_ELAPSED_S_ON_TICK = rx.Var.create(
    f"e => {{if({LOCAL_TIME_ELAPSED_S_VALUE} >= {TimerState.total_time_s._var_name_unwrapped}) {{"
    # Update the backend state to stop the timer.
    + rx.utils.format.format_event_chain(
        rx.EventChain(
            events=[
                TimerState.set_tick_interval_ms(0),
                TimerState.set_time_elapsed_s(LOCAL_TIME_ELAPSED_S_VAR),
            ],
        )
    ) +
    "} else {"
    # Update the frontend state to show timer progress
    f"{SET_LOCAL_TIME_ELAPSED_S_VALUE}({LOCAL_TIME_ELAPSED_S_VALUE} + 1)}}}}"
)._replace(
    _var_type=rx.EventChain,
    merge_var_data=LOCAL_TIME_ELAPSED_S_VAR_DATA,
)
LOCAL_TIME_ELAPSED_S_RESET = rx.Var.create(
    f"e => {{{SET_LOCAL_TIME_ELAPSED_S_VALUE}(0.001); " +
    rx.utils.format.format_event_chain(
        rx.EventChain(
            events=[
                TimerState.set_reset_timer(False),
            ],
        ),
    ) + "}",
)._replace(
    _var_type=rx.EventChain,
    merge_var_data=LOCAL_TIME_ELAPSED_S_VAR_DATA,
)


def timer(**box_props) -> rx.Component:
    color_props = {
        "color": "var(--accent-10)",
    }
    timer = rx.box(
        rx.cond(
            TimerState.reset_timer,
            rx.moment(interval=1, on_change=LOCAL_TIME_ELAPSED_S_RESET, display="none"),
        ),
        circular_progressbar_with_children(
            rx.vstack(
                #rx.cond(
                #    TimerState.time_elapsed_s > 0,
                    #rx.heading(rx.moment(date=TimerState.time_elapsed_s.to(str), unix=True, format="mm:ss"), **color_props),
                rx.heading(
                    rx.moment(
                        date=LOCAL_TIME_ELAPSED_S_VAR.to(str),
                        unix=True,
                        format="mm:ss",
                        interval=TimerState.tick_interval_ms,
                        on_change=LOCAL_TIME_ELAPSED_S_ON_TICK,
                    ),
                    **color_props,
                ),
                #    rx.heading("00:00", **color_props),
                #),
                rx.cond(
                    TimerState.is_running,
                    rx.icon("pause", **color_props),
                    rx.icon("play", **color_props),
                ),
                align="center",
            ),
            value=LOCAL_TIME_ELAPSED_S_VAR,
            max_value=TimerState.total_time_s,
        ),
        on_click=TimerState.toggle_running,
        **box_props,
    )
    return IntegralFragment.create(timer)
