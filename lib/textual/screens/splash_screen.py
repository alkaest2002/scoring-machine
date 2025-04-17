from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Markdown

md ="""
# Markdown Document

This is an example of Textual's `Markdown` widget.

## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!
"""

class SplashScreen(Screen):

    CSS = """
    
    Markdown {
        background: transparent;
        padding: 0;
    }

    MarkdownH1 {
        content-align: left middle;
    }
"""

    def __repr__(self) -> str:
        return "splashScreen"

    def compose(self) -> ComposeResult:
        yield Markdown(md)
