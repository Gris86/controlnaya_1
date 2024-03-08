from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Footer, Header, Static
from textual.widget import Widget

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

    def __init__(self, note: notes.Note):
        super().__init__(classes="NoteWidget")
        self.note = note
    
    def compose(self) -> ComposeResult:
        yield NoteWidget__Title(self.note)
        yield Static(classes="spacer")
        yield Button("Редактировать", id=f"edit{self.note.note_id.hex}", variant="primary")
        yield Button("Удалить", id=f"delete_{self.note.note_id.hex}", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        print(f"button pressed: {event.button.id}")
        if event.button.id.startswith("delete_"):
            note_id = event.button.id.removeprefix("delete_") + ".json"
            utils.delete_note(note_id)
        

class NotesApp(App):
    CSS_PATH = "tui.tcss"

    BINDINGS = [("ctrl+d", "toggle_dark", "Переключить тёмный режим"), ("ctrl+n", "new_note", "Создать новую заметку")]

    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        for x in utils.get_all_notes():
            yield NoteWidget(x)
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
    
    def action_new_note(self) -> None:
        pass