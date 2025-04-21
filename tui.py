import pandas as pd
from textual import on
from textual.app import App
from textual.reactive import reactive
from lib.textual.screens.splash_screen import SplashScreen
from lib.textual.screens.file_screen import FileScreen
from lib.textual.screens.score_screen import ScoringScreen
from lib.textual.screens.end_screen import EndScreen

class MyApp(App):

    CSS = """
    Screen {
        padding: 1 2 1 2;
        align: left top;
        background: transparent
    }
    """

    SCREENS = {
        "splashScreen": SplashScreen,
        "fileScreen": FileScreen,  
        "scoreScreen": ScoringScreen,
        "endScreen": EndScreen,
    }

    BINDINGS = [
        ("left", "app.change_screen(-1)", "move to previous screen"),
        ("right", "app.change_screen(1)", "move to next screen"),
    ]

    current_job: reactive[dict] = reactive({
        "selected_path": None,
        "df": None
    })

    current_screen : reactive[str] = reactive("splashScreen")

    condition_to_switch_screen: reactive[dict[str, bool]] = reactive({
        "scoreScreen": False
    })

    def __init__(self):
        self.screens_list = list(self.SCREENS.keys())
        self.number_of_screens = len(self.screens_list)
        super().__init__()

    def watch_current_screen(self, new_screen: str) -> None:
        self.switch_screen(new_screen)

    def on_mount(self) -> None:
        self.theme = "gruvbox"
        self.push_screen("splashScreen")

    def action_change_screen(self, offset: int) -> None:
        old_screen_index = self.screens_list.index(self.screen.__repr__())
        new_screen_index = old_screen_index + offset
        new_screen_index = max(0, min(self.number_of_screens -1, new_screen_index))
        new_screen = self.screens_list[new_screen_index]
        if self.condition_to_switch_screen.get(new_screen, True):
            self.current_screen = new_screen

    @on(FileScreen.CSVTree.NodeHighlighted)
    def on_file_screen_node_highlighted(self, event: FileScreen.CSVTree.NodeHighlighted) -> None:
        selected_path = event.node.data.path # type: ignore
        selected_path_is_file = selected_path.is_file()
        self.condition_to_switch_screen["scoreScreen"] = selected_path_is_file
        self.current_job["selected_path"] = selected_path if selected_path_is_file else None
        self.current_job["df"] = pd.read_csv(selected_path) if selected_path_is_file else None
        
if __name__ == "__main__":
    app = MyApp()
    app.run()