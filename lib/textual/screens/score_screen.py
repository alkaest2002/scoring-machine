from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

class ScoringScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Static("Scoring Screen")