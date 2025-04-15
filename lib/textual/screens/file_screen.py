from pathlib import Path
from typing import Iterable
from textual import on
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree, Static

class CSVTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.suffix.__eq__(".csv")]

class FileScreen(Screen):

    CSS = """

    FileScreen > * {
        margin: 1;
    }

    CSVTree {
        height: auto;
        padding: 2;
        background: #000;
    }

    SelectedFile {
        height: 1;
    }

"""

    def __repr__(self) -> str:
        return "fileScreen"

    selected_file = reactive("", layout=True)
    
    def watch_selected_file(self, newValue: str):
        self.query_one("#selected_file", Static).update(newValue)
    
    @on(CSVTree.FileSelected)
    def on_file_selected(self, event: CSVTree.FileSelected) -> None:
        self.selected_file = event.path.name

    def compose(self) -> ComposeResult:
        yield Label("Scegli il file contenente i dati dei test da siglare e premi <invio>")
        yield CSVTree("./data")
        yield Label("File selezionato:")
        yield Static(id="selected_file")