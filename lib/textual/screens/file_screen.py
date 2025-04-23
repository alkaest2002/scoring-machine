import csv

from rich.text import Text
from pathlib import Path
from typing import Generator, Iterable
from textual.widget import Widget
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree, Static, Footer, Rule
from textual.containers import HorizontalGroup, VerticalGroup

class FileScreen(Screen):

    def __repr__(self) -> str:
        return "fileScreen"

    class CSVTree(DirectoryTree):
        def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
            filter_condition1 = lambda x: x.suffix.__eq__(".csv")
            filder_condition2 = lambda x: x.is_dir() and x.name[0] != "."
            return [path for path in paths if any([filter_condition1(path), filder_condition2(path)])]
        
    class CSVPreview(Widget):
        data_provider = reactive("...")

        def compose(self) -> ComposeResult:
            with VerticalGroup():
                yield Label(Text("Prima riga", style="italic"))
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

        & #left_pane {
            width: 40%;
            height: auto;
            background: $panel;
            margin-right: 1;
            border-right: tall $foreground;

            & > CSVTree { 
                padding: 1 2;
                background: transparent;
            }
        }

        & #data_preview_widget Label {
            margin-bottom: 1;
        }
    }
"""
    
    BINDINGS = [
        ("<", "change_screen(-1)", "prec"),
        (">", "change_screen(1)", "succ"),
    ]

    current_path = reactive[Path](Path("./data"))
    
    current_filename = reactive[str]("nessuno", layout=True)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="current_path_group"):
            yield Label("Seleziona il file CSV da siglare:")
            yield Static("nessuno", id="current_path")
        yield Rule(line_style="dashed")
        with HorizontalGroup(id="current_tree_group"):
            with HorizontalGroup(id="left_pane"):
                yield self.CSVTree(str(Path("./data")))
            yield self.CSVPreview(id="data_preview_widget")
        yield Footer(show_command_palette=False)

    def on_mount(self) -> None:
        self.CSVTree.show_root = False  # type: ignore
        
    def watch_current_filename(self, current_filename: str):
        current_path_group = self.query_one("#current_path")
        data_preview = self.query_one("#data_preview_widget")
        if current_filename != "nessuno":
            current_path = self.current_path / current_filename
            with open(current_path) as f:
                csv_reader = csv.reader(f)
                rows_count = sum(1 for _ in f) -1
                f.seek(0)
                rows_count = min(1000, rows_count)
                current_path_group.update(f"{current_filename} ({rows_count} righe)") # type: ignore
                current_path_group.styles.color = "#03AC13"
                data_preview.data_provider = csv_reader # type: ignore
        else:
            current_path_group.update("nessuno") # type: ignore
            current_path_group.styles.color = "#fb4934"
            data_preview.data_provider = "..." # type: ignore

    def on_tree_node_highlighted(self, event) -> None:
        current_path = event.node.data.path
        self.current_path = current_path.parent
        self.current_filename = current_path.name if current_path.is_file() else "nessuno" 