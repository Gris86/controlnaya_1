from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.events import Event
from textual.widgets import Button, Footer, Header, Static
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message

import note as notes
import utils

class NoteWidget__Title(Static):
    note: notes.Note

    def __init__(self, note: notes.Note):
        self.note = note
        super().__init__(f"{self.note.title}\n\nСоздана в: {self.note.timestamp.day}.{self.note.timestamp.month}.{self.note.timestamp.year} {self.note.timestamp.hour}:{self.note.timestamp.minute}:{self.note.timestamp.second}", classes="NoteWidget__Title")
    
    def compose(self) -> ComposeResult:
        return super().compose()

class NoteWidget(Widget):
    note: notes.Note

    def __init__(self, note: notes.Note, app):
        super().__init__(classes="NoteWidget")
        self.note = note
        self.note_app = app
    
    def compose(self) -> ComposeResult:
        yield NoteWidget__Title(self.note)
        yield Static(classes="spacer")
        yield Button("Редактировать", id=f"edit{self.note.note_id.hex}", variant="primary")
        yield Button("Удалить", id=f"delete_{self.note.note_id.hex}", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        # raise Exception(event.button.id)
        if event.button.id.startswith("delete_"):
            note_id = event.button.id.removeprefix("delete_")
            utils.delete_note(note_id)
        self.post_message(NotesApp.NotesUpdated())

class NotesApp(App):
    class NotesUpdated(Message):
        pass

    CSS_PATH = "tui.tcss"

    BINDINGS = [("ctrl+d", "toggle_dark", "Переключить тёмный режим"), ("ctrl+n", "new_note", "Создать новую заметку"), ("ctrl+c", "quit", "Выйти")]

    ENABLE_COMMAND_PALETTE = False

    all_notes: list[notes.Note] = reactive(utils.get_all_notes())

    def compose(self) -> ComposeResult:
        self.widgets = []
        yield Header(show_clock=True)
        with ScrollableContainer(id="container"):
            for x in self.all_notes:
                yield NoteWidget(x, self)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
    
    def action_new_note(self) -> None:
        pass

    def on_notes_app_notes_updated(self, message):
        self.all_notes = utils.get_all_notes()
        container = self.query_one("#container", ScrollableContainer)
        container.remove_children()
        container.mount_all([NoteWidget(x, self) for x in self.all_notes])