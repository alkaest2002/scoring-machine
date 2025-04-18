from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Button

class EndScreen(Screen):

    def __repr__(self) -> str:
        return "endScreen"

    CSS = """
    Label {
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        dock: bottom;
    }

"""

    def compose(self) -> ComposeResult:
        yield Label("Fine")
        yield Button("esci", variant="primary")

    def on_button_pressed(self):
        self.app.exit()