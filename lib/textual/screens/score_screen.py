import asyncio
from email import message
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Label, Rule, Footer, Button,  RadioButton, RadioSet, Static
from textual.containers import HorizontalGroup, VerticalGroup
from textual.reactive import reactive
from lib.data_container import DataContainer
from lib.data_provider import DataProvider
from lib.reporter import Reporter
from lib.sanitizer import Sanitizer
from lib.scorer import Scorer
from lib.standardizer import Standardizer

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
    class Notifier(Widget):
        message = reactive[str]("")

        def render(self) -> str:
            return self.message

    
    CSS = """

    HorizontalGroup {
        margin-bottom: 1;
    }

    #current_path_group {

        #current_path_label {
            color: #03AC13;
            padding-left: 1;
            align: left middle;
        }
    }

    VerticalGroup {
    
        & > * {
            margin-bottom: 1;
            margin-left: 1;
        }

        RadioSet {
            background: $panel;
            width: 100%;

            & > RadioButton {
            
                & > .toggle--button {
                background: transparent
                }

                &.-selected {
                    background: transparent;
                }
            }
        }
    }
   
"""

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato:")
            yield Label(id="current_path_label")
        yield Rule(line_style="dashed")
        with VerticalGroup():
            with RadioSet(id="compute_standard_scores"):
                yield RadioButton("calcola punteggi standard", name="True", value=True)
                yield RadioButton("non calcolare punteggi standard", name="False")
            with RadioSet(id="output_type"):
                yield RadioButton("tipo di output: pdf", name="pdf", value=True)
                yield RadioButton("tipo di output: csv", name="csv")
                yield RadioButton("tipo di output: json", name="json")
            with RadioSet(id="split_reports"):
                yield RadioButton("genera report unico", name="False", value=True)
                yield RadioButton("genera report singoli", name="True")
            yield Button("avvia siglatura", id="score_button", variant="primary")
            yield ScoringScreen.Notifier(id="job_status")
        yield Footer(show_command_palette=False)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.query_one("#job_status").message = "" # type: ignore
        self.app.current_job[event.control.id] = bool(event.pressed.name) if event.pressed.name in ["True", "False"] else event.pressed.name  # type: ignore

    def on_input_submitted(self) -> None:
        next_element_to_focus = self.query_one("#compute_standard_scores_group")
        self.set_focus(next_element_to_focus)

    async def score_data(self) -> None:
        try:
            data_provider: DataProvider = DataProvider(self.app.current_job["current_test"]) # type: ignore
            data_container: DataContainer = DataContainer(data_provider)
            data_container: DataContainer = Sanitizer(data_container).sanitize_data()
            data_container: DataContainer = Scorer(data_container).compute_raw_related_scores()
            if self.app.current_job["compute_standard_scores"]: # type: ignore
                data_container: DataContainer = Standardizer(data_container).compute_standard_scores()
            if self.app.current_job["output_type"] != "pdf": # type: ignore
                data_container.persist(type=self.app.current_job["output_type"]) # type: ignore
            else:
                Reporter(data_container).generate_report(
                    assessment_date=self.app.current_job["assessment_date"],  # type: ignore
                    split_reports=self.app.current_job["split_reports"] # type: ignore
                )
            self.query_one("#job_status").message = "Siglatura conclusa." # type: ignore
        except Exception as e:
            print(e)
            self.query_one("#job_status").message = f"Si è verificato il seguente errore: {e}" # type: ignore

    def on_button_pressed(self):
        self.query_one("#job_status").message = "Siglatura in corso. Prego, attendere..." # type: ignore
        self.run_worker(self.score_data, exclusive=True)

    def on_screen_resume(self) -> None:
        self.query_one("#current_path_label").update(self.app.current_job["current_path_label"]) # type: ignore
        self.query_one("#job_status").message = "" # type: ignore
        self.query_one("#score_button").focus()
