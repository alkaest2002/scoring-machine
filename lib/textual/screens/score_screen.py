from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"

    def compose(self) -> ComposeResult:
        yield Label(f"Scoring file --> {self.app.selected_file_path}") # type: ignore

    def on_screen_resume(self) -> None:
        self.query_one("Label").update(f"Scoring file --> {self.app.selected_file_path}") # type: ignore