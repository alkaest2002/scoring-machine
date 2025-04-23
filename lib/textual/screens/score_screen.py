import re
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Static, Rule, Footer, Input, Button,  RadioButton, RadioSet
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

    VerticalGroup {
    
        & > * {
            margin-bottom: 1;
        }

        Button {
            margin-left: 1;
        }
    
        RadioSet {
            background: transparent;
            width: 100%;
        }
    }
   
"""

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato:")
            yield Static(id="current_path")
        yield Rule(line_style="dashed")
        with VerticalGroup():
            with RadioSet(id="compute_standard_scores_group"):
                yield RadioButton("calcola punteggi standard", id="compute_standard_scores", value=True)
                yield RadioButton("non calcolare punteggi standard", id="do_not_compute_standard_scores")
            with RadioSet(id="output_type_group"):
                yield RadioButton("tipo di output: pdf", id="output_type_pdf", value=True)
                yield RadioButton("tipo di output: csv", id="output_type_csv")
                yield RadioButton("tipo di output: json", id="output_type_json")
            with RadioSet(id="split_reports_group"):
                yield RadioButton("genera report singoli", id="split_reports_yes", value=True)
                yield RadioButton("genera report unico", id="split_reports_no")
            yield Button("avvia siglatura", id="score_button", variant="primary")
        yield Footer(show_command_palette=False)

    def on_input_submitted(self) -> None:
        next_element_to_focus = self.query_one("#compute_standard_scores_group")
        self.set_focus(next_element_to_focus)

    def on_button_pressed(self, event: Button.Pressed):
        print("------------->", event.handler_name)

    def get_current_path_label(self) -> str:
        current_path = self.app.current_job["current_path"] # type: ignore
        df = self.app.current_job["df"] # type: ignore
        return f"{current_path.name} ({ df.shape[0] } righe)" # type: ignore
    
    def on_screen_resume(self) -> None:
        current_path_element = self.query_one("#current_path")
        current_path_element.update(self.get_current_path_label()) # type: ignore
