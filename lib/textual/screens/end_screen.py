from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button

class EndScreen(Screen):

    CSS = """
    Label {
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        dock: bottom;
    }

"""

    def __repr__(self) -> str:
        return "endScreen"

    def compose(self) -> ComposeResult:
        yield Label("Fine")
        yield Button("esci", variant="primary")

    @on(Button.Pressed)
    def exit_from_app(self):
        self.app.exit()