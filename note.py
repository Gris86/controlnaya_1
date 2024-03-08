import json
import uuid
from datetime import datetime

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
        self.second = second
    
    @staticmethod
    def from_json(json_string: str):
        parsed_json = json.loads(json_string)
        return NoteTimestamp(*parsed_json)
    
    @staticmethod
    def current_time():
        today = datetime.now()
        return NoteTimestamp(today.year, today.month, today.day, today.hour, today.minute, today.second)

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
        parsed_json = json.loads(json_string)
        return Note(
            NoteTimestamp(*parsed_json['timestamp']),
            parsed_json['title'],
            parsed_json['body'],
            note_id=uuid.UUID(
                hex=parsed_json['note_id']
            )
        )
