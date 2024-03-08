"""
Создаёт много заметок в целях тестирования.
"""

import utils
import note

for i in range(50):
    utils.write_note(note.Note(note.NoteTimestamp.current_time(), f"test{i}", f"ABCDEFG\n{i}"))