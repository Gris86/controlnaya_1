import textual.command
import rich.text
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Grid, Horizontal, Vertical
from functools import partial
from textual.events import Event
from textual.widgets import Button, Footer, Header, Static, Label, TextArea, Input
from textual.command import DiscoveryHit, Hit, Hits, Provider, CommandPalette
from textual.types import IgnoreReturnCallbackType
from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.screen import ModalScreen

import note as notes
import utils

class NoteWidget__Title(Static):
    note: notes.Note

    def __init__(self, note: notes.Note):
        self.note = note
        super().__init__(f"{self.note.title}\n\nСоздана в: {self.note.timestamp.day}.{self.note.timestamp.month}.{self.note.timestamp.year} {self.note.timestamp.hour}:{self.note.timestamp.minute}:{self.note.timestamp.second}", classes="NoteWidget__Title")
    
    def compose(self) -> ComposeResult:
        return super().compose()

class EditNote(ModalScreen):
    is_creating: bool = False
    note: notes.Note

    def __init__(self, note_app, note: notes.Note, is_creating: bool = False, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)
        self.is_creating = is_creating
        self.note = note
        self.note_app = note_app
    
    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Создать заметку" if self.is_creating else "Изменить заметку", id="title"),
            Label("Название:"),
            Input(self.note.title, placeholder="Название", id="note_name"),
            Label("Содержимое:"),
            TextArea(self.note.body, id="note_body", tab_behavior="indent", show_line_numbers=True, soft_wrap=True),
            Grid(
                Button("Создать" if self.is_creating else "Сохранить", variant="primary", id="save"),
                Button("Отмена", variant="error", id="cancel"),
                id="dialog_buttons"
            ),
            id="dialog"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.note_app.pop_screen()
        if event.button.id == "save":
            self.note.title = self.query_one("#note_name", Input).value
            self.note.body = self.query_one("#note_body", TextArea).text
            if self.is_creating:
                self.note.timestamp = notes.NoteTimestamp.current_time()
            utils.write_note(self.note)
            self.note_app.all_notes = utils.get_all_notes()
            self.note_app.post_message(NotesApp.NotesUpdated())
            self.note_app.pop_screen()

class NoteWidget(Widget):
    note: notes.Note

    def __init__(self, note: notes.Note, app):
        super().__init__(classes="NoteWidget")
        self.note = note
        self.note_app = app
    
    def compose(self) -> ComposeResult:
        yield NoteWidget__Title(self.note)
        yield Static(classes="spacer")
        yield Button("Редактировать", id=f"edit_{self.note.note_id.hex}", variant="primary")
        yield Button("Удалить", id=f"delete_{self.note.note_id.hex}", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("delete_"):
            note_id = event.button.id.removeprefix("delete_")
            utils.delete_note(note_id)
        if event.button.id.startswith("edit_"):
            note_id = event.button.id.removeprefix("edit_")
            for x in utils.get_all_notes():
                if x.note_id.hex == note_id:
                    self.note_app.push_screen(EditNote(self.note_app, x, is_creating=False))
                    break
            return
        self.post_message(NotesApp.NotesUpdated())

class Commands(Provider):

    @property
    def commands(self) -> tuple[tuple[str, IgnoreReturnCallbackType, str], ...]:
        """The system commands to reveal to the command palette."""
        return (
            (
                "Изменить тему",
                self.app.action_toggle_dark,
                "Включить или выключить тёмный режим",
            ),
            (
                "Выйти",
                self.app.action_quit,
                "Выходит из приложения",
            ),
            (
                "Поиск заметок по имени",
                self.app.action_search_by_title,
                "Запустить поиск заметок по имени"
            ),
            (
                "Поиск заметок по дате и времени",
                self.app.action_search_by_time,
                "Запустить поиск заметок по дате и времени"
            )
        )

    async def discover(self) -> Hits:
        for name, runnable, help_text in self.commands:
            yield DiscoveryHit(
                name,
                runnable,
                help=help_text,
            )

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for name, runnable, help_text in self.commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text,
                )

class NotesSearchByNameProvider(Provider):
    async def discover(self) -> Hits:
        for note in utils.get_all_notes():
            yield DiscoveryHit(
                note.title,
                partial(self.app.push_screen, EditNote(note_app=self.app, note=note)),
                help=f"Заметка создана {note.timestamp.day}.{note.timestamp.month}.{note.timestamp.year} в {note.timestamp.hour}:{note.timestamp.minute}:{note.timestamp.second}",
            )
    
    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for note in utils.get_all_notes():
            if (match := matcher.match(note.title)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(note.title),
                    partial(self.app.push_screen, EditNote(note_app=self.app, note=note)),
                    help=f"Заметка создана {note.timestamp.day}.{note.timestamp.month}.{note.timestamp.year} в {note.timestamp.hour}:{note.timestamp.minute}:{note.timestamp.second}",
                )

class NotesSearchByDateProvider(Provider):
    async def discover(self) -> Hits:
        for note in utils.get_all_notes():
            yield DiscoveryHit(
                note.title,
                partial(self.app.push_screen, EditNote(note_app=self.app, note=note)),
                help=f"Дата и время создания: {self.stringify_timestamp(note.timestamp)}",
            )

    @staticmethod
    def stringify_timestamp(timestamp: notes.NoteTimestamp):
        return f"{timestamp.day}.{timestamp.month}.{timestamp.year} {timestamp.hour}:{timestamp.minute}:{timestamp.second}"

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for note in utils.get_all_notes():
            stringified_timestamp = self.stringify_timestamp(note.timestamp)
            if (match := matcher.match(stringified_timestamp)) > 0:
                yield Hit(
                    match,
                    note.title,
                    partial(self.app.push_screen, EditNote(note_app=self.app, note=note)),
                    help=f"Дата и время создания: {self.stringify_timestamp(note.timestamp)}",
                )

class NotesSearchByName(CommandPalette):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(id="--input"):
                yield textual.command.SearchIcon()
                yield textual.command.CommandInput(placeholder="Поиск по названию заметок...")
                if not self.run_on_select:
                    yield Button("\u25b6")
            with Vertical(id="--results"):
                yield textual.command.CommandList()
                yield textual.command.LoadingIndicator()

    @property
    def _provider_classes(self) -> set[type[Provider]]:
        return {NotesSearchByNameProvider}

class NotesSearchByDate(NotesSearchByName):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(id="--input"):
                yield textual.command.SearchIcon()
                yield textual.command.CommandInput(placeholder=f"Формат времени: {NotesSearchByDateProvider.stringify_timestamp(notes.NoteTimestamp.current_time())}")
                if not self.run_on_select:
                    yield Button("\u25b6")
            with Vertical(id="--results"):
                yield textual.command.CommandList()
                yield textual.command.LoadingIndicator()

    @property
    def _provider_classes(self) -> set[type[Provider]]:
        return {NotesSearchByDateProvider}

class NotesApp(App):
    class NotesUpdated(Message):
        pass

    CSS_PATH = "tui.tcss"

    COMMANDS = {Commands}

    BINDINGS = [("ctrl+d", "toggle_dark", "Переключить тёмный режим"), ("ctrl+n", "new_note", "Создать новую заметку"), ("ctrl+c", "quit", "Выйти")]

    all_notes: list[notes.Note] = reactive(utils.get_all_notes())

    def action_search_by_title(self) -> None:
        self.run_worker(self._action_search_by_title())

    async def _action_search_by_title(self) -> None:
        result = await self.push_screen_wait(NotesSearchByName())
        if result:
            result()
    
    def action_search_by_time(self) -> None:
        self.run_worker(self._action_search_by_time())

    async def _action_search_by_time(self) -> None:
        result = await self.push_screen_wait(NotesSearchByDate())
        if result:
            result()

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
        self.push_screen(EditNote(self, notes.Note(notes.NoteTimestamp.current_time(), "", ""), is_creating=True))

    def on_notes_app_notes_updated(self, _):
        self.all_notes = utils.get_all_notes()
        container = self.query_one("#container", ScrollableContainer)
        container.remove_children()
        container.mount_all([NoteWidget(x, self) for x in self.all_notes])