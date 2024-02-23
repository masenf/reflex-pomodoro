"""This module wraps the npm package `react-circular-progressbar`."""

import inspect
from typing import Literal

import reflex as rx


class CircularProgressbar(rx.Component):
    library = "react-circular-progressbar"
    tag = "CircularProgressbar"

    # Completion value of the progressbar, from minValue to maxValue. Required.
    value: rx.Var[int | float]

    # Minimum value of the progressbar. Default: 0.
    min_value: rx.Var[int | float]

    # Maximum value of the progressbar. Default: 100.
    max_value: rx.Var[int | float]

    # Text to display inside progressbar. Default: ''.
    text: rx.Var[str]

    # Width of circular line relative to total width of component, a value from 0-100. Default: 8.
    stroke_width: rx.Var[int]

    # Whether to display background color. Default: false.
    background: rx.Var[bool]

    # Padding between background circle and path/trail relative to total width of component. Only used if background is true. Default: 0.
    background_padding: rx.Var[int]

    # Whether to rotate progressbar in counterclockwise direction. Default: false.
    counter_clockwise: rx.Var[bool]

    # Number from 0-1 representing ratio of the full circle diameter the progressbar should use. Default: 1.
    circle_ratio: rx.Var[float]

    # Object allowing overrides of classNames of each svg subcomponent (root, trail, path, text, background). Enables styling with react-jss.
    classes: rx.Var[dict]

    # Object allowing customization of styles of each svg subcomponent (root, trail, path, text, background).
    styles: rx.Var[dict]

    # The radix themes color scheme to use.
    color_scheme: rx.Var[rx.radix.base.LiteralAccentColor]

    def _get_imports(self) -> dict[str, list[rx.utils.imports.ImportVar]]:
        return rx.utils.imports.merge_imports(
            super()._get_imports(),
            {
                "": {
                    rx.utils.imports.ImportVar(
                        tag="react-circular-progressbar/dist/styles.css",
                    ),
                },
                self.library: {
                    rx.utils.imports.ImportVar(
                        tag="buildStyles",
                    ),
                },
            },
        )

    @staticmethod
    def build_styles(
        color_scheme: rx.radix.base.LiteralAccentColor | Literal["accent"] = "accent",
        rotation: float | None = None,
        stroke_linecap: Literal["butt", "round"] | None = None,
        text_size: str | None = None,
        path_transition: str | None = None,
        path_transition_duration: float | None = None,
        text_color: str | None = None,
        path_color: str | None = None,
        trail_color: str | None = None,
        background_color: str | None = None,
    ) -> rx.Var[dict]:
        bs = {}
        if rotation is not None:
            bs["rotation"] = rotation
        if stroke_linecap is not None:
            bs["strokeLinecap"] = stroke_linecap
        if text_size is not None:
            bs["textSize"] = text_size
        if path_transition is not None:
            bs["pathTransition"] = path_transition
        if path_transition_duration is not None:
            bs["pathTransitionDuration"] = path_transition_duration
        bs["textColor"] = text_color or f"var(--{color_scheme}-10)"
        bs["pathColor"] = path_color or f"var(--{color_scheme}-8)"
        bs["trailColor"] = trail_color or f"var(--{color_scheme}-2)"
        if background_color is not None:
            bs["backgroundColor"] = background_color
        return rx.Var.create(f"buildStyles({bs})").to(dict)

    @classmethod
    def create(cls, *children, **props) -> rx.Component:
        style_props = {
            prop: props.pop(prop)
            for prop in inspect.signature(cls.build_styles).parameters
            if prop in props
        }
        props.setdefault("styles", cls.build_styles(**style_props))
        return super().create(*children, **props)


class CircularProgressbarWithChildren(CircularProgressbar):
    tag = "CircularProgressbarWithChildren"


circular_progressbar = CircularProgressbar.create
circular_progressbar_with_children = CircularProgressbarWithChildren.create
