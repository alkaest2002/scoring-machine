from pathlib import Path
from typing import Iterable
from textual import on
from textual.events import Event
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.suffix.__eq__(".csv")]

class FileScreen(Screen):

    def __repr__(self) -> str:
        return "fileScreen"
    
    selected_file = reactive("")

    @on(FilteredDirectoryTree.FileSelected)
    def on_file_selected(self, event: FilteredDirectoryTree.FileSelected) -> None:
        print("****** FILE SELECTED ******", event.path.name)
        self.selected_file = event.path.name

    def compose(self) -> ComposeResult:
        yield Label("Scegli il file contenente i dati dei test da siglare e premi invio")
        yield FilteredDirectoryTree("./data")
        yield Label("File selezionato:")
        yield Label(self.selected_file)