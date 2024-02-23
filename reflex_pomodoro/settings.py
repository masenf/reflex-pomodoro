"""Settings for the Pomodoro timer."""
import json

import reflex as rx


_fields = {
    "work_time_m": "Work Time (minutes)",
    "break_time_m": "Break Time (minutes)",
    "long_break_time_m": "Long Break Time (minutes)",
    "long_break_interval": "Long Break Interval",
}


class SettingsState(rx.State):
    work_time_m: int = 25
    break_time_m: int = 5
    long_break_time_m: int = 15
    long_break_interval: int = 4

    settings_json: str = rx.LocalStorage()
    dialog_is_open: bool = False

    def load_settings(self):
        if self.settings_json:
            try:
                settings = json.loads(self.settings_json)
                for field in _fields:
                    setattr(self, field, int(settings.get(field, getattr(self, field))))
            except ValueError:
                self.reset()  # reset to defaults on error

        # Populate form fields
        if self.dialog_is_open:
            return [rx.set_value(field, getattr(self, field)) for field in _fields]

    def save_settings(self, form_data):
        for key, value in form_data.items():
            setattr(self, key, int(value))

        self.settings_json = json.dumps(
            {field: getattr(self, field) for field in _fields}
        )

        self.dialog_is_open = False


def settings_form():
    return rx.form(
        rx.vstack(
            *[
                rx.hstack(
                    description,
                    rx.spacer(),
                    rx.input(
                        id=field,
                        type="number",
                    ),
                    wrap="wrap",
                    width="100%",
                )
                for field, description in _fields.items()
            ],
            rx.hstack(
                rx.dialog.close(
                    rx.button("Cancel", type="button", color_scheme="red"),
                ),
                rx.spacer(),
                rx.button("Save"),
                padding_top="1em",
                width="100%",
            ),
            width="100%",
        ),
        on_submit=SettingsState.save_settings,
        on_mount=SettingsState.load_settings,
    )


def settings_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(rx.icon("settings")),
        ),
        rx.dialog.content(
            rx.dialog.title("Settings"),
            settings_form(),
        ),
        open=SettingsState.dialog_is_open,
        on_open_change=SettingsState.set_dialog_is_open,
    )
