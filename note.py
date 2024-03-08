import json
import uuid

class NoteTimestamp:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

    def to_json(self) -> list:
        return [self.year, self.month, self.day, self.hour, self.minute, self.second]
    
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int, second: int) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.secound = second
    
    @staticmethod
    def from_json(json_string: str):
        parsed_json = json.parse(json_string)
        return NoteTimestamp(*parsed_json)

class Note:
    timestamp: NoteTimestamp
    note_id: uuid.UUID
    title: str
    body: str

    def __init__(self, timestamp: NoteTimestamp, title: str, body: str, *, note_id: uuid.UUID = None):
        if note_id == None:
            note_id = uuid.uuid4()
        self.note_id = note_id
        self.timestamp = timestamp
        self.title = title
        self.body = body
    
    def to_json(self) -> dict:
        return {
            'note_id': self.note_id.hex,
            'timestamp': self.timestamp.to_json(),
            'title': self.title,
            'body': self.body
        }
    
    @staticmethod
    def from_json(json_string: str):
        parsed_json = json.parse(json_string)
        return Note(NoteTimestamp.from_json(parsed_json['timestamp']), parsed_json['title'], parsed_json['body'], note_id=uuid.UUID(json_string['note_id']))
