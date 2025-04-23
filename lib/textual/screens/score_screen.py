import re
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Rule, Footer, Input
from textual.containers import HorizontalGroup, VerticalGroup

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
    CSS = """

    HorizontalGroup {
        margin-bottom: 1;
    }

    #current_path_group {

        #current_path {
            color: #03AC13;
            padding-left: 1;
            align: left middle;
        }
    }

    DataTable {
        background: transparent;

        & .datatable--header {
            background: transparent;
        }
    }
"""

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato:")
            yield Static(id="current_path")
        yield Rule(line_style="dashed")
        with VerticalGroup():
            yield Input(id="test_id")
        yield Footer(show_command_palette=False)

    def get_current_path_label(self) -> str:
        current_path = self.app.current_job["current_path"] # type: ignore
        df = self.app.current_job["df"] # type: ignore
        return f"{current_path.name} ({ df.shape[0] } righe)" # type: ignore
    
    def get_test_id_from_path(self) -> re.Match:
        available_tests = [ f.name for f in Path("./lib/tests").iterdir() if f.is_dir() and not f.name.startswith('_')]
        matches = [re.search(test, self.app.current_job["current_path"].name) for test in available_tests] # type: ignore
        return [match for match in matches if match][0]
    
    def on_screen_resume(self) -> None:
        current_path_element = self.query_one("#current_path")
        current_path_element.update(self.get_current_path_label()) # type: ignore
        current_test_element = self.query_one("#test_id")
        test_id_match = self.get_test_id_from_path()
        current_test_element.value =  test_id_match.group(0) if test_id_match else "" # type: ignore
