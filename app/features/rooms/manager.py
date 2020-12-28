import sys
from typing import List

from sqlalchemy.orm.attributes import flag_modified


class Session:
    id: str


class Room:
    id: str
    participants: List[Session] = []


class RoomsManager:
    def __init__(self, room_model, db):
        self.model = room_model
        self.connection = db

    def join(self, sid_participant: str, sid_room: str) -> None:
        room = self.model.query.filter_by(code=sid_room).first()

        if room is not None:
            if len(room.participants) > 0:
                room.participants.append(sid_participant)
                flag_modified(room, "participants")
                self.connection.session.merge(room)
                self.connection.session.flush()
                self.connection.session.commit()
                return

        room = self.model(sid_room, [sid_participant])
        self.connection.session.add(room)
        self.connection.session.commit()

    def participants(self, sid_room) -> []:
        room = self.model.query.filter_by(code=sid_room).first()

        if room is not None:
            if len(room.participants) > 0:
                return room.participants
            else:
                return []
        return []

    def get_room(self, token):
        room = self.model.query.filter(self.model.participants.contains([token])).first()

        if room is not None:
            return room.code

        return None
