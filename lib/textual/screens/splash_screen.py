from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Markdown, Footer

md ="""
# THE SCORING MACHINE PROJECT

Applicativo per la siglatura di questionari psicologici.

## Cosa dovrai fare:

- Selezionare il file CSV (nella cartella data) contenente i dati da siglare.
- Configurare il tipo di siglatura.
- Avviare la siglatura e la generazione dei report.

Premi il tasto command + freccia destra |CMD →| per andare avanti.
"""

class SplashScreen(Screen):

    def __repr__(self) -> str:
        return "splashScreen"

    CSS = """
    Markdown {
        background: transparent;
        margin: 0;
        padding: 0;
    }

    MarkdownH1 {
        content-align: left middle;
        margin: 0;
        padding: 0;
    }
"""
    BINDINGS = [
        Binding("ctrl+e", "app.switch_screen('fileScreen')", "succ", key_display="CMD →"),
    ]

    def compose(self) -> ComposeResult:
        yield Markdown(md)
        yield Footer(show_command_palette=False)
