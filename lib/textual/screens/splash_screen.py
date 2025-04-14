from typing import Literal
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

class SplashScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Static("Splash screen")
