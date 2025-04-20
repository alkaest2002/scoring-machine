import pandas as pd

from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, DataTable, Rule, Footer
from textual.containers import HorizontalGroup

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
    CSS = """

    HorizontalGroup {
        margin-bottom: 1;
    }

    #selected_path_group {

        #selected_path {
            color: green;
            padding-left: 1;
            align: left middle;
        }
    }

    Rule {
        color: #fff;
    }

    DataTable {
        background: transparent;
        width: 100%;

        & .datatable--header {
            background: transparent;
        }
    }
"""

    BINDINGS = [
        ("<", "change_screen(-1)", "prec."),
        (">", "change_screen(1)", "succ"),
    ]
    
    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="selected_path_group"):
            yield Label("File selezionato ---> ")
            yield Static(id="selected_path")
        with HorizontalGroup(id="count_group"):
            yield Label("Dati di processare ---> ")
            yield Static(id="count")
        yield Rule(line_style="solid")
        yield DataTable()
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        data_table = self.query_one(DataTable)
        data_table.header_height = 2
        data_table.show_cursor = False

    def on_screen_resume(self) -> None:
        
        # Refresh selected file
        file_to_score_path = self.app.current_job["selected_path"] # type: ignore
        self.query_one("#selected_path").update(file_to_score_path.name) # type: ignore
        
        # Open file
        try:

            # Load data
            df = pd.read_csv(Path("./data/") / file_to_score_path)

            # Update count
            count = min(1000, df.shape[0])
            self.query_one("#count").update(str(count)) # type: ignore
        
            # Data table
            columns_slicer = list(range(0,5)) + [-1]
            header = df.iloc[0, columns_slicer].index.to_list()
            header = header[:-1] + ["..."] + [header[-1]]
            rows = df.iloc[0:5, columns_slicer]
            rows.insert(rows.shape[1]-1, "...", "...")
            if df.shape[0] > 5:
                new_row = pd.DataFrame([["..."]*len(rows.columns)], columns=rows.columns)
                rows = pd.concat([ rows, new_row ])
            table = self.query_one(DataTable)
            table.clear(columns=True)
            table.add_columns(*header)
            table.add_rows(rows.values.tolist()) # type: ignore
        
        # On error loading
        except Exception as e:
            print(e)