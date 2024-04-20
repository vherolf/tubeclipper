from pathlib import Path
import asyncio

from pytube import YouTube
from pytube.streams import Stream
from pytube.exceptions import RegexMatchError

import pyperclip
from time import monotonic

from textual.screen import ModalScreen
from textual.containers import Horizontal, ScrollableContainer, Widget
from textual.reactive import reactive
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import (
    Header,
    Footer,
    Static,
    Label,
)

class Url(Static):
    def __init__(self, author:str, title:str, url: str) -> None:
        self.author = author
        self.title = title
        self.url = url
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(self.title, id="title")
            yield Label(self.author, id="author")
            yield Label(self.url, id="url")
        

class TubeClipper(App):
    def __init__(self) -> None:
        self.last_url = ""
        self.test_mode = False
        self.download_location = Path("~/Music").expanduser()
        super().__init__()

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), 
                ("t","test_mode","Test Mode on (no download)"),
                ("q","quit","Quit"),
                ]
    CSS_PATH = "tube-clipper.css"
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(id="url")
        with ScrollableContainer(id="history"):
            yield Url("author","title","url")
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.periodic) 
        
    async def periodic(self):
        while True:
            url = pyperclip.paste()
            if url.startswith("https://www.youtube.com/"):
                pyperclip.copy("")
                yt = YouTube(url)
                author = yt.author
                title = yt.title
                download_location = self.download_location
                if not self.test_mode:
                    yt.streams.get_audio_only().download(output_path= download_location, filename= f"{author} - {title}.mp4".replace('/','-') ) 
                new_entry = Url(author, title, url)
                self.notify(f"Downloaded {author} {title}", title=title)
                self.query_one("#history").mount(new_entry)
                self.last_url = url

            await asyncio.sleep(0.5)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_test_mode(self) -> None:
        """An action to toggle dark mode."""
        self.test_mode = not self.test_mode
        if self.test_mode:
            self.app.query_one(Footer).highlight_key = "t"
        else:
            self.app.query_one(Footer).highlight_key = None
        self.bell()

    def action_quit(self) -> None:
        self.exit()
        
        self.bell()
        def check_quit(quit: bool) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()


if __name__ == "__main__":
    app = TubeClipper()
    app.run()
