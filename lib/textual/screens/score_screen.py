from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"

    def compose(self) -> ComposeResult:
        yield Label(f"Scoring file --> {self.app.store["files"]}") # type: ignore