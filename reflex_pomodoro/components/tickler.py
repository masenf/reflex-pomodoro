"""Tickler is a custom reflex component that tracks "ticks" on the frontend only."""

from typing import Any, Dict
import uuid

import reflex as rx
from reflex.components.moment import Moment

from .use_state import useState


class Tickler(Moment):
    """Keep track of the number of ticks that have occurred locally.

    Update the backend TimerState when the limit is reached.
    """

    value: rx.Var[float]
    set_value: rx.Var[str]
    value_name: rx.Var[str]

    tick_limit: rx.Var[int] = 0
    tick_should_reset: rx.Var[bool] = False

    def get_event_triggers(self) -> Dict[str, Any]:
        return super().get_event_triggers() | {
            "on_tick_limit": lambda tick_value: [tick_value],
            "on_reset": lambda: [],
        }

    def _exclude_props(self) -> set[str]:
        # All props and triggers are used internally and should not be passed to Moment
        return (
            self.get_props().union({"on_tick_limit", "on_reset"}) - Moment.get_props()
        )

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        instance_id = str(uuid.uuid4()).replace("-", "_")
        props["value"], props["set_value"] = useState(
            f"localTimeElapsed_{instance_id}", 0.001
        )
        props["value_name"] = props["value"]._var_name_unwrapped
        props["display"] = props.get("display", "none")

        # Create interim component to access "on_tick"
        comp = super().create(*children, **props)

        # Wire up the on change event to the tick logic.
        props["on_change"] = comp.on_tick()
        if props.get("tick_should_reset") is not None:
            props["interval"] = rx.cond(
                props["tick_should_reset"],
                1,
                props.get("interval", 0),
            )

        # Create the final component.
        return super().create(*children, **props)

    def on_tick(self) -> rx.Var:
        """JS logic to handle each tick on the frontend."""
        on_reset = self.event_triggers["on_reset"] or ""
        if isinstance(on_reset, rx.EventChain):
            on_reset_backend = rx.utils.format.format_event_chain(on_reset)
            on_reset = (
                f"if({self.tick_should_reset._var_name_unwrapped})"
                "{"
                f"{self.set_value}(0.001); {on_reset_backend};"
                "return"
                "}"
            )

        on_tick_limit = self.event_triggers["on_tick_limit"] or ""
        if isinstance(on_tick_limit, rx.EventChain):
            on_tick_limit = rx.utils.format.format_event_chain(on_tick_limit).replace(
                ":_tick_value",
                f":{self.value_name._var_name_unwrapped}",
            )

        return rx.Var.create(
            "e => {"
            f"{on_reset}"
            f"if({self.value_name} < {self.tick_limit._var_name_unwrapped})"
            "{" +
            # Update the frontend state with latest tick count.
            f"{self.set_value}({self.value_name} + 1)" + "} else {"
            # Update the backend state when limit is reached.
            f"{on_tick_limit}"
            "}"
            "}",
        )._replace(
            _var_type=rx.EventChain,
            merge_var_data=self.value._var_data,
        )


tickler = Tickler.create
