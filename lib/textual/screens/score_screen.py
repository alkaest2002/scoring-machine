from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Rule, Footer
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
        yield Footer(show_command_palette=False)

    def get_selected_path_label(self) -> str:
        selected_path = self.app.current_job["selected_path"] # type: ignore
        df = self.app.current_job["df"] # type: ignore
        return f"{selected_path.name} ({ df.shape[0] } righe)" # type: ignore
 
    def on_screen_resume(self) -> None:
        self.query_one("#selected_path").update(self.get_selected_path_label()) # type: ignore