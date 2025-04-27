from typing import Optional
from enum import Enum

from textual.app import ComposeResult
from textual.screen import Screen
from textual import work
from textual.worker import Worker, WorkerState
from textual.reactive import reactive
from textual.widgets import Label, Rule, Footer, Button,  RadioButton, RadioSet, Static
from textual.containers import HorizontalGroup, VerticalGroup
from lib.data_container import DataContainer
from lib.data_provider import DataProvider
from lib.reporter import Reporter
from lib.sanitizer import Sanitizer
from lib.scorer import Scorer
from lib.standardizer import Standardizer

class StatusMessages(Enum):
    CANCELLED = "Operazione di siglatura annullata."
    ERROR = "Ooops! Errore di siglatura."
    PENDING = "Siglatura in attesa"
    RUNNING = "Siglatura in corso. Prego attendere..."
    SUCCESS = "Siglatura conclusa con successo."

class ScoringScreen(Screen):

    def __repr__(self) -> str:
        return "scoreScreen"
    
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
    worker: Optional[Worker] = reactive(None) # type: ignore

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato:")
            yield Label(id="current_path_label")
        yield Rule(line_style="dashed")
        with VerticalGroup(id="current_job_options"):
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
        with VerticalGroup(id="current_job"):
            yield Button("avvia siglatura", id="score_button", variant="primary")
            yield Static(id="job_status")
        yield Footer(show_command_palette=False)

    def on_screen_resume(self) -> None:
        self.reset_worker()
        self.query_one("#current_path_label").update(self.app.current_job["current_path_label"]) # type: ignore
        self.query_one("#score_button").focus()
  
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.reset_worker()
        self.app.current_job[event.control.id] = bool(event.pressed.name) if event.pressed.name in ["True", "False"] else event.pressed.name  # type: ignore

    def on_button_pressed(self):
        self.worker = self.score_data() # type: ignore

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        message = StatusMessages[event.state.name]
        for w in self.query(RadioSet):
            w.disabled = event.state.name == WorkerState.RUNNING.name
        self.query_one(Button).disabled = event.state.name == WorkerState.RUNNING.name
        self.notify_status(message)

    def reset_worker(self):
        if self.worker:
            self.notify_status(StatusMessages.PENDING)
            self.worker.cancel()
    
    def notify_status(self, message: Enum):
        self.query_one("#job_status").update(message.value) # type: ignore

    @work(exclusive=True, thread=True)
    async def score_data(self) -> None:
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
        
