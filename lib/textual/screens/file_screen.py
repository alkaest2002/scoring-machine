from pathlib import Path
from typing import Iterable
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree, Static
from textual.containers import HorizontalGroup

class FileScreen(Screen):

    class CSVTree(DirectoryTree):
        def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
            return [path for path in paths if path.suffix.__eq__(".csv") or path.is_dir()]
        
    CSS = """

    FileScreen > * {
        margin: 1;
    }

    CSVTree {
        height: auto;
        padding: 2;
        background: rgb(18,18,18);
    }

    SelectedFile {
        height: 1;
    }

    HorizontalGroup > Label  {
        margin-right: 1
    }

"""
    selected_file = reactive("", layout=True)

    def __repr__(self) -> str:
        return "fileScreen"

    def on_mount(self) -> None:
        self.CSVTree.show_root = False # type: ignore
        
    
    def watch_selected_file(self, selected_file: str):
        self.query_one("#selected_file", Static).update(selected_file)
    
    def on_directory_tree_file_selected(self, event: CSVTree.FileSelected) -> None:
        print(self.CSVTree.FileSelected.handler_name)
        self.selected_file = event.path.name

    def compose(self) -> ComposeResult:
        yield Label("Scegli il file contenente i dati dei test da siglare e premi <invio>")
        with HorizontalGroup():
            yield Label("File selezionato:")
            yield Static(id="selected_file")
        yield self.CSVTree("./data")