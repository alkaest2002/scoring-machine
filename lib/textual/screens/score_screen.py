from typing import Optional
from enum import Enum
from datetime import date

from textual import work
from textual.reactive import reactive
from textual.binding import Binding
from textual.app import ComposeResult
from textual.screen import Screen
from textual.worker import Worker, WorkerState
from textual.widgets import Label, Rule, Footer, Button,  RadioButton, RadioSet, Static
from textual.containers import HorizontalGroup, VerticalGroup
from lib.data_container import DataContainer
from lib.data_provider import DataProvider
from lib.reporter import Reporter
from lib.sanitizer import Sanitizer
from lib.scorer import Scorer
from lib.standardizer import Standardizer

class StatusMessages(Enum):
    PENDING = ""
    RUNNING = "Siglatura in corso. Prego attendere..."
    SUCCESS = "Siglatura conclusa con successo."
    ERROR = "Ooops! Errore di siglatura."
    CANCELLED = "Operazione di siglatura annullata."

class ScoringScreen(Screen):

    CSS = """

    #current_path_group {
        margin-bottom: 1;

        #current_path_label {
            color: #03AC13;
            padding-left: 1;
            align: left middle;
        }
    }

    #current_job_options {
        margin-bottom: 1;

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
    
    #current_job {
        Button {
            margin-bottom: 1
        }
    }
"""
    BINDINGS = [
        Binding("q", "app.switch_screen('fileScreen')", "prec"),
    ]
    
    worker: Optional[Worker] = reactive(None) # type: ignore

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato:")
            yield Label(id="current_path_label")
        yield Rule(line_style="dashed")
        with VerticalGroup(id="current_job_options"):
            with RadioSet(id="compute_standard_scores"):
                yield RadioButton("calcola punteggi standard", id="compute_standard_scores_true", name="True", value=True)
                yield RadioButton("non calcolare punteggi standard", id="compute_standard_scores_false", name="False")
            with RadioSet(id="output_type"):
                yield RadioButton("tipo di output: pdf",  id="output_type_pdf", name="pdf", value=True)
                yield RadioButton("tipo di output: csv",  id="output_type_csv", name="csv")
                yield RadioButton("tipo di output: json", id="output_type_json", name="json")
            with RadioSet(id="split_reports"):
                yield RadioButton("genera report unico", id="split_reports_false",  name="False", value=True)
                yield RadioButton("genera report singoli", id="split_reports_true",  name="True")
        with VerticalGroup(id="current_job"):
            yield Button("avvia siglatura", id="score_button", variant="primary")
            yield Static(id="job_status")
        yield Footer(show_command_palette=False)

    def on_screen_suspend(self):
       self.reset_worker()
    
    def on_screen_resume(self) -> None:
        self.reset_worker()
        self.query_one("#current_path_label").update(self.app.current_job["current_path_label"]) # type: ignore
        self.query_one("#score_button").focus()
  
    def on_radio_set_changed(self):
        self.reset_worker()
    
    def on_button_pressed(self):
        self.worker = self.score_data()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        message = StatusMessages[event.state.name]
        disable_widget = event.state.name == WorkerState.RUNNING.name
        for w in [ *self.query(RadioSet), self.query_one(Button)]:
            w.disabled = disable_widget
        self.notify_status(message)
        event.stop()

    def reset_worker(self):
        self.notify_status(StatusMessages.PENDING)
        if self.worker:
            self.worker.cancel()
    
    def notify_status(self, message: Enum):
        self.query_one("#job_status").update(message.value) # type: ignore

    @work(name="score_worker", exclusive=True, thread=True)
    async def score_data(self) -> None:
        data_provider: DataProvider = DataProvider(self.app.current_job["current_test"]) # type: ignore
        data_container: DataContainer = DataContainer(data_provider)
        data_container: DataContainer = Sanitizer(data_container).sanitize_data()
        data_container: DataContainer = Scorer(data_container).compute_raw_related_scores()
        if self.query_one("#compute_standard_scores_true").value: # type: ignore
            data_container: DataContainer = Standardizer(data_container).compute_standard_scores()
        if self.query_one("#output_type_pdf").value: # type: ignore
            Reporter(data_container).generate_report(
                assessment_date=date.today().strftime("%d/%m/%Y"),  # type: ignore
                split_reports=self.query_one("#split_reports_true").value # type: ignore
            )
        else:
            output_type = self.query_one("#output_type").pressed_button.name # type: ignore
            data_container.persist(type=output_type) # type: ignore
