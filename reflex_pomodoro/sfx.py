import reflex as rx


def sound_fx() -> rx.Component:
    return rx.script(
        """
        var work_done = new Audio("/work_done.wav")
        var break_done = new Audio("/break_done.wav")
        function playFromStart (sfx) {sfx.load(); sfx.play()}"""
    )


def work_done_sfx() -> rx.event.EventSpec:
    return rx.call_script("playFromStart(work_done)")


def break_done_sfx() -> rx.event.EventSpec:
    return rx.call_script("playFromStart(break_done)")
