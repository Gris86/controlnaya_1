import os.path
import json

import note

def init():
    if not os.path.exists("notes"):
        os.mkdir("notes")
    else:
        if not os.path.isdir("notes"):
            raise NotADirectoryError("Файл с именем notes уже существует, однако, это не папка.")

def read_note(filename: str) -> note.Note:
    with open(os.path.join(os.getcwd(), 'notes', filename), 'r') as f:
        return note.Note.from_json(f.read())

def write_note_to_file(note: note.Note, filename: str):
    with open(os.path.join(os.getcwd(), 'notes', filename), 'w') as f:
        json.dump(note.to_json(), f)

def write_note(note: note.Note):
    "Имя файла автоматически генерируется."
    write_note_to_file(note, note.note_id.hex + ".json")

def list_note_filenames() -> list[str]:
    return os.listdir("notes")

def get_all_notes() -> list[note.Note]:
    lst = []
    for x in list_note_filenames():
        lst.append(read_note(x))
    return lst

def delete_note(note_id: str):
    for x in list_note_filenames():
        x_note = read_note(x)
        if x_note.note_id.hex == note_id:
            os.unlink(os.path.join(os.getcwd(), "notes", x))