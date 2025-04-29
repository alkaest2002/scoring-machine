from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual.widgets import Markdown, Footer

md = """
# THE SCORING MACHINE PROJECT

Applicativo per la siglatura di questionari psicologici.

## Cosa dovrai fare:

- Selezionare il file CSV della cartella _data_ contenente i questionari da siglare.
- Configurare il tipo di siglatura che sarà effettuata.
- Avviare la siglatura e la generazione dei report.

Premi la lettera |w| per andare avanti.
"""

class SplashScreen(Screen):

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
        Binding("w", "app.switch_screen('fileScreen')", "succ"),
    ]

    def compose(self) -> ComposeResult:
        yield Markdown(md)
        yield Footer(show_command_palette=False)
