import pandas as pd

from pathlib import Path
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
        Binding("escape", "quit", "esci", priority=True, key_display="esc"),
    ]

    current_job: reactive[dict] = reactive({
        "current_path": None,
        "current_path_label": None,
        "current_test": None,
    })

    def on_mount(self) -> None:
        self.theme = "gruvbox"
        self.push_screen("splashScreen")

    @work(name="score_worker", exclusive=True, thread=True)
    async def load_df(self, current_path: Path) -> str:
        current_df = pd.read_csv(current_path, nrows=1000)
        current_path_label = f"{current_path.name} ({current_df.shape[0]} righe)"
        return current_path_label

    @on(FileScreen.CSVTree.NodeHighlighted)
    async def on_file_screen_node_highlighted(self, event: FileScreen.CSVTree.NodeHighlighted) -> None:
        current_path = event.node.data.path # type: ignore
        if current_path.is_file():
            self.current_job["current_path"] = current_path
            self.current_job["current_test"] = current_path.name.split("_")[0]
            self.load_df(current_path)
    
    @on(Worker.StateChanged)
    def on_worker_state_changed(self, event: Worker.StateChanged):
        if  event.state == WorkerState.SUCCESS:
            self.current_job["current_path_label"] = event.worker.result

if __name__ == "__main__":
    app = MyApp()
    app.run()