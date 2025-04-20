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
            condition1 = lambda x: x.suffix.__eq__(".csv")
            condition2 = lambda x: x.is_dir() and x.name[0] != "."
            return [path for path in paths if any([condition1(path), condition2(path)])]
        
    CSS = """
    CSVTree {
        height: auto;
        background: transparent;
    }

    #current_path_group {
    
        height: 1;
        margin: 1 0;

        #current_path {
            color: red;
            padding-left: 1;
            align: left middle;
        }
    }
"""
    
    current_path: reactive[str] = reactive[str]("nessuno", layout=True)

    def on_mount(self) -> None:
        self.CSVTree.show_root = False # type: ignore
        
    def watch_current_path(self, current_path: str):
        element = self.query_one("#current_path", Static)
        element.update(current_path)
        element.styles.color = "red" if current_path == "nessuno" else "green"

    def on_tree_node_highlighted(self, event) -> None:
        current_path = event.node.data.path
        self.current_path = current_path.name if current_path.is_file() else "nessuno"

    def compose(self) -> ComposeResult:
        yield Static("Seleziona il file CSV da siglare e premi <invio>")
        with HorizontalGroup(id="current_path_group"):
            yield Label("File selezionato ---> ")
            yield Static(id="current_path")
        yield self.CSVTree(str(Path("./data")))