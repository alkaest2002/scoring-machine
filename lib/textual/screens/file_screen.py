from pathlib import Path
from typing import Iterable
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, DirectoryTree, Static
from textual.containers import HorizontalGroup

class FileScreen(Screen):

    def __repr__(self) -> str:
        return "fileScreen"

    class CSVTree(DirectoryTree):
        def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
            return [path for path in paths if path.suffix.__eq__(".csv") or path.is_dir()]
        
    CSS = """
    CSVTree {
        height: auto;
        background: transparent;
    }

    #selected_file_group {
    
        height: 1;
        margin: 1 0;

        #selected_file {
            color: red;
            padding-left: 1;
            align: left middle;
        }
    }
"""
    
    selected_file: reactive[str] = reactive[str]("nessuno", layout=True)

    def on_mount(self) -> None:
        self.CSVTree.show_root = False # type: ignore
        
    def watch_selected_file(self, selected_file: str):
        self.query_one("#selected_file", Static).update(selected_file)
    
    def on_directory_tree_file_selected(self, event: CSVTree.FileSelected) -> None:
        self.selected_file = event.path.name
        self.query_one("#selected_file").styles.color = "green"

    def compose(self) -> ComposeResult:
        yield Static("Scegli il file CSV contenente i dati dei questionari/test da siglare e premi < invio >")
        with HorizontalGroup(id="selected_file_group"):
            yield Label("File selezionato ---> ")
            yield Static(id="selected_file")
        yield self.CSVTree(str(Path("./data")))