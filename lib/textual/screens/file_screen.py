import csv

from rich.text import Text
from pathlib import Path
from typing import Generator, Iterable, Optional
from textual.binding import Binding
from textual.widget import Widget
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree, Static, Footer, Rule
from textual.containers import HorizontalGroup, VerticalGroup

AVAILABLE_TESTS = [ f.name for f in Path("./lib/tests").iterdir() if f.is_dir() and not f.name.startswith('_')]

class FileScreen(Screen):

    class CSVTree(DirectoryTree):
        def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
            filter_cond_A = lambda x: any([f"{test.lower()}_data.csv" == x.name.lower() for test in AVAILABLE_TESTS])
            filter_cond_B = lambda x: x.is_dir() and x.name[0] != "."
            return [path for path in paths if any([filter_cond_A(path), filter_cond_B(path)])]
        
    class CSVPreview(Widget):
        
        data_provider = reactive[str]("...")

        def compose(self) -> ComposeResult:
            with VerticalGroup():
                yield Label(Text("Prima riga", style="italic"), id="data_preview_label")
                yield Static("...", id="data_preview")

        def watch_data_provider(self, newVal: str | Generator) -> None:
            element = self.query_one("#data_preview")
            if isinstance(newVal, str):
                element.update(newVal)  # type: ignore
            else:
                first_row = [ f"{k}: {v}" for k, v in zip(next(newVal), next(newVal)) ]
                element.update(", ".join(first_row)) # type: ignore
               
    CSS = """

    Screen {
        layout: vertical;
    }
   
    #current_path_group {
        
        margin-bottom: 1;
        height: 1;

        #current_path {
            color: red;
            padding-left: 1;
            align: left middle;
        }
    }

    #current_tree_group {
        
        height: 1fr;
        margin-bottom: 1;
        padding-left: 0;
        layout: horizontal;

        & > VerticalGroup {
            width: 40%;
            height: auto;
            background: $panel;
            margin-right: 1;
            border-right: tall $foreground;

            & Static {
                padding: 1 2;
            }

            & > CSVTree { 
                padding: 1 2;
                background: transparent;
            }
        }

        CSVPreview Label {
            margin-bottom: 1;
        }
    }
"""
    
    BINDINGS = [
        Binding("p", "go_to('splashScreen')", "prec"),
        Binding("s", "go_to('scoreScreen')", "succ"),
    ]
    
    current_path = reactive[Optional[Path]](None, bindings=True)

    def __init__(self) -> None:
        super().__init__()
        self.set_reactive(FileScreen.current_path, Path("./data"))
    
    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("Seleziona il file CSV da siglare:")
            yield Static("nessuno")
        yield Rule(line_style="dashed")
        with HorizontalGroup(id="current_tree_group"):
            with VerticalGroup():
                yield Static("Elenco dei file compatibili (i.e., <nome_test>_data.csv).")
                yield self.CSVTree(str(Path("./data")))
            yield self.CSVPreview()
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.CSVTree.show_root = False  # type: ignore

    def action_go_to(self, screen: str) -> None:
        self.app.switch_screen(screen)

    def check_action(self, action: str, parameters: tuple[object, ...]):
        if action == "go_to" and parameters[0] == "scoreScreen" and self.current_path.is_dir(): # type: ignore
            return None
        return True
    
    def watch_current_path(self, current_path: Path):
        current_path_label = self.query_one("#current_path_group Static")
        csv_preview = self.query_one(self.CSVPreview)
        if current_path.is_file():
            with open(current_path) as f:
                csv_reader = csv.reader(f)
                rows_count = sum(1 for _ in f) -1
                f.seek(0)
                rows_count = min(1000, rows_count)
                current_path_label.update(f"{current_path.name} ({rows_count} righe)") # type: ignore
                current_path_label.styles.color = "#03AC13"
                csv_preview.data_provider = csv_reader # type: ignore
        else:
            current_path_label.update("nessuno") # type: ignore
            current_path_label.styles.color = "#fb4934"
            csv_preview.data_provider = "..." # type: ignore
        
    def on_tree_node_highlighted(self, event) -> None:
        self.current_path = event.node.data.path
