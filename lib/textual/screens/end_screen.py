from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button

class EndScreen(Screen):

    def __repr__(self) -> str:
        return "endScreen"

    def compose(self) -> ComposeResult:
        yield Static("Fine")
        yield Button("esci")

    @on(Button.Pressed)
    def exit_from_app(self):
        self.app.exit()