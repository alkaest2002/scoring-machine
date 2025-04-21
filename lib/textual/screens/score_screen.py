import pandas as pd

from pathlib import Path
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Label, Static, DataTable, Rule, Footer
from textual.containers import HorizontalGroup
from rich.text import Text

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
    CSS = """

    HorizontalGroup {
        margin-bottom: 1;
    }

    #selected_path_group {

        #selected_path {
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

    BINDINGS = [
        ("<", "change_screen(-1)", "prec."),
        (">", "change_screen(1)", "succ"),
    ]

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="selected_path_group"):
            yield Label("File selezionato:")
            yield Static(id="selected_path")
        yield Rule(line_style="dashed")
        yield DataTable()
        yield Footer(show_command_palette=False)

    def get_selected_path_label(self, df: pd.DataFrame) -> str:
        return f"{self.app.current_job['selected_path'].name} ({min(1000, df.shape[0])} righe)" # type: ignore
    
    def load_df(self) -> pd.DataFrame:
        file_to_score_path = Path("./data/") / self.app.current_job["selected_path"] # type: ignore
        return pd.read_csv(file_to_score_path)

    def on_mount(self) -> None:
        data_table = self.query_one(DataTable)
        data_table.header_height = 1
        data_table.show_cursor = False
 
    def on_screen_resume(self) -> None:
        df = self.load_df()
        self.query_one("#selected_path").update(self.get_selected_path_label(df)) # type: ignore
        try:
            empty_placeholder = "-"
            number_of_rows_to_show = 10
            number_of_columns_to_show = 10
            columns_slicer = list(range(0, number_of_columns_to_show)) + [-1] # Limit columns to show (keep last)
            header = df.iloc[0, columns_slicer].index.to_list()
            header = [*header[:-1], empty_placeholder, header[-1]]
            rows_to_show = df.iloc[0:number_of_rows_to_show, columns_slicer] # Limit rows to show
            rows_to_show.insert(rows_to_show.shape[1]-1, empty_placeholder, empty_placeholder)
            last_row = df.iloc[[-1], columns_slicer]
            if df.shape[0] > number_of_rows_to_show:
                empty_row = pd.DataFrame([[empty_placeholder]*len(rows_to_show.columns)], columns=rows_to_show.columns)
                rows_to_show = pd.concat([ rows_to_show, empty_row, last_row ])
            table = self.query_one(DataTable)
            table.clear(columns=True)
            for idx, column in enumerate(header):
                width = 10 if idx < 2 else 3
                table.add_column(Text(str(column), justify="center"), width=width)
            for row in rows_to_show.values.tolist():
                styled_row = [Text(str(cell), justify="center") for cell in row]
                table.add_row(*styled_row)
        
        # On error loading
        except Exception as e:
            print(e)