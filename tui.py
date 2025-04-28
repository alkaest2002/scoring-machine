from pathlib import Path
import pandas as pd

from textual import on, work
from textual.worker import Worker, WorkerState
from textual.app import App
from textual.binding import Binding
from textual.reactive import reactive
from lib.textual.screens.splash_screen import SplashScreen
from lib.textual.screens.file_screen import FileScreen
from lib.textual.screens.score_screen import ScoringScreen

class MyApp(App):

    CSS = """
    Screen {
        padding: 1 2;
        align: left top;
        background: transparent
    }
    """

    SCREENS = {
        "splashScreen": SplashScreen,
        "fileScreen": FileScreen,  
        "scoreScreen": ScoringScreen,
    }

    BINDINGS = [
        Binding("ctrl+a", "change_screen(-1)", "prec", priority=True, key_display="CMD ←"),
        Binding("ctrl+e", "change_screen(1)", "succ", priority=True, key_display="CMD →"),
        Binding("escape", "quit", "esci", priority=True, key_display="ESC"),
    ]

    current_job: reactive[dict] = reactive({
        "current_path": None,
        "current_path_label": None,
        "current_test": None,
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
        capped_new_screen_index = max(0, min(self.number_of_screens -1, new_screen_index))
        new_screen = self.screens_list[capped_new_screen_index]
        if self.condition_to_switch_screen.get(new_screen, True):
            self.current_screen = new_screen

    @work(name="score_worker", exclusive=True, thread=True)
    async def load_df(self, current_path: Path) -> str:
        current_df = pd.read_csv(current_path, nrows=1000)
        current_path_label = f"{current_path.name} ({current_df.shape[0]} righe)"
        return current_path_label

    @on(FileScreen.CSVTree.NodeHighlighted)
    async def on_file_screen_node_highlighted(self, event: FileScreen.CSVTree.NodeHighlighted) -> None:
        current_path = event.node.data.path # type: ignore
        if current_path.is_file():
            self.condition_to_switch_screen["scoreScreen"] = True
            self.current_job["current_path"] = current_path
            self.current_job["current_test"] = current_path.name.split("_")[0]
            self.load_df(current_path)
    
    @on(Worker.StateChanged)
    def on_wroker_state_changed(self, event: Worker.StateChanged):
        if  event.state == WorkerState.SUCCESS:
            self.current_job["current_path_label"] = event.worker.result

if __name__ == "__main__":
    app = MyApp()
    app.run()