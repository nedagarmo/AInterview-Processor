from typing import List


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
                self.connection.session.commit()
                return

        room = self.model(sid_room, [sid_participant])
        self.connection.session.add(room)
        self.connection.session.commit()

    def participants(self, sid_room):
        room = self.model.query.filter_by(code=sid_room).first()

        if room is not None:
            if len(room.participants) > 0:
                return room.participants
            else:
                return []
        return []
