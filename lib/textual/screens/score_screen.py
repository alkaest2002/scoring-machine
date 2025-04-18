from pathlib import Path
import pandas as pd

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, DataTable
from textual.containers import HorizontalGroup

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
    CSS = """
    #selected_file_group {
    
        margin-bottom: 1;

        #selected_file {
            color: green;
            padding-left: 1;
            align: left middle;
        }
    }

    DataTable {
        background: transparent;
    }
"""
    
    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="selected_file_group"):
            yield Label("File selezionato ---> ")
            yield Static(id="selected_file")
        yield DataTable()

    def on_mount(self) -> None:
        self.query_one(DataTable).cursor_type = 'row'

    def on_screen_resume(self) -> None:
        
        # Refresh selected file
        file_to_score_path = self.app.current_job["selected_file_path"] # type: ignore
        self.query_one("#selected_file").update(str(file_to_score_path)) # type: ignore
        
        # Refresh data table
        df = pd.read_csv(Path("./data/") / file_to_score_path)
        slicer = list(range(0,10)) + [-1]
        header = df.iloc[0, slicer].index.to_list()
        header = header[:-1] + ["..."] + header[-1:]
        rows = df.iloc[0:5, slicer]
        rows.insert(rows.shape[1] -1, "...", "...")
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns(*header)
        table.add_rows(rows.values.tolist()) # type: ignore