from typing import Any
from textual.app import App
from textual.events import Key
from textual.reactive import reactive
from lib.textual.screens.splash_screen import SplashScreen
from lib.textual.screens.file_screen import FileScreen
from lib.textual.screens.score_screen import ScoringScreen
from lib.textual.screens.end_screen import EndScreen

class MyApp(App):

    CSS = """
    Screen {
        align: center middle;
    }

    Static {
        text-align: center;
    }
    """

    SCREENS = {
        "splash": SplashScreen,
        "file": FileScreen,  
        "score": ScoringScreen,
        "end": EndScreen,
    }

    BINDINGS = [
        ("left", "change_screen('left')", "move to previous screen"),
        ("right", "change_screen('right')", "move to next screen"),
    ]

    store = reactive[dict[str, Any]]({
        "files": []
    })

    screens_cycle = reactive[dict[str, dict[str, str]]]({
        "SplashScreen()":  { "left": "splash", "right": "file" },
        "FileScreen()":    { "left": "splash", "right": "score" },
        "ScoringScreen()": { "left": "file",   "right": "end" },
        "EndScreen()":     { "left": "score",  "right": "end" },
    })

    def watch_screen(self):
        print("ciao")

    def on_mount(self) -> None:
        self.push_screen("splash")

    def action_change_screen(self, key: str) -> None:
        current_screen_navigation = self.screens_cycle.get(self.screen.__repr__())
        screen_to_switch_to = current_screen_navigation[key] # type: ignore
        self.switch_screen(screen_to_switch_to)

if __name__ == "__main__":
    app = MyApp()
    app.run()