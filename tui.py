from multiprocessing.spawn import old_main_modules
import pandas as pd
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
        padding: 1;
    }
    """

    SCREENS = {
        "splashScreen": SplashScreen,
        "fileScreen": FileScreen,  
        "scoreScreen": ScoringScreen,
        "endScreen": EndScreen,
    }

    BINDINGS = [
        ("left", "change_screen(-1)", "move to previous screen"),
        ("right", "change_screen(1)", "move to next screen"),
    ]

    store = reactive[dict[str, Any]]({
        "files": []
    })

    current_screen = reactive("splashScreen")

    def __init__(self):
        self.screens_list = list(self.SCREENS.keys())
        self.number_of_screens = len(self.screens_list)
        super().__init__()

    def watch_current_screen(self, new_screen: str) -> None:
        self.switch_screen(new_screen)

    def on_mount(self) -> None:
        self.push_screen("splashScreen")

    def action_change_screen(self, offset: int) -> None:
        old_screen_index = self.screens_list.index(self.screen.__repr__())
        new_screen_index = old_screen_index + offset
        new_screen_index = max(0, min(self.number_of_screens -1, new_screen_index))
        self.current_screen = self.screens_list[new_screen_index]

if __name__ == "__main__":
    app = MyApp()
    app.run()