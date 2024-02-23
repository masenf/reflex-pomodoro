"""Tickler is a custom reflex component that tracks "ticks" on the frontend only."""

from typing import Any
import uuid

from jinja2 import Environment

import reflex as rx

from .use_state import useState


ON_TICK_JINJA2 = Environment().from_string("""
useEffect(() => {
    if ({{tick_should_reset}}) {
        {{set_value}}(0);
        {{on_reset}};
        return;
    }
    if ({{interval}} > 0) {
        const interval_id = setInterval(() => {
            if ({{value}} < {{tick_limit}}) {
                {{set_value}}({{value}} + 1);
            } else {
                {{on_tick_limit}};
            }
        }, {{interval}});
        return () => clearInterval(interval_id);
    }
}, [{{interval}}, {{tick_limit}}, {{tick_should_reset}}, {{value}}]);
""")


class Tickler(rx.Component):
    """Keep track of the number of ticks that have occurred locally.

    Update the backend TimerState when the limit is reached.
    """
    library = "worker-timers"

    interval: rx.Var[int] = 0
    tick_limit: rx.Var[int] = 0
    tick_should_reset: rx.Var[bool] = False

    # These props are used internally, do not override them.
    value: rx.Var[int]
    set_value: rx.Var[str]

    def _get_imports(self) -> dict[str, list[rx.utils.imports.ImportVar]]:
        return {
            "worker-timers": [
                rx.utils.imports.ImportVar(tag="setInterval"),
                rx.utils.imports.ImportVar(tag="clearInterval"),
            ]
        }

    def _get_hooks(self) -> set[str]:
        """Overriding the default hook because order matters!"""
        on_reset = self.event_triggers["on_reset"] or ""
        if isinstance(on_reset, rx.EventChain):
            on_reset = rx.utils.format.format_event_chain(on_reset)

        on_tick_limit = self.event_triggers["on_tick_limit"] or ""
        if isinstance(on_tick_limit, rx.EventChain):
            on_tick_limit = rx.utils.format.format_event_chain(on_tick_limit).replace(
                ":_tick_value",
                f":{self.value._var_name_unwrapped}",
            )

        return ON_TICK_JINJA2.render(
            interval=self.interval._var_name_unwrapped,
            tick_limit=self.tick_limit._var_name_unwrapped,
            tick_should_reset=self.tick_should_reset._var_name_unwrapped,
            value=self.value._var_name_unwrapped,
            set_value=self.set_value._var_name_unwrapped,
            on_reset=on_reset,
            on_tick_limit=on_tick_limit,
        )

    def get_event_triggers(self) -> dict[str, Any]:
        return {
            "on_tick_limit": lambda tick_value: [tick_value],
            "on_reset": lambda: [],
        }

    def render(self) -> dict:
        return {}

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        instance_id = str(uuid.uuid4()).replace("-", "_")
        props["value"], props["set_value"] = useState(
            name=f"localTimeElapsed_{instance_id}",
            initial_value=0,
        )

        # Create the final component.
        return super().create(*children, **props)


tickler = Tickler.create
