from typing import List


class Session:
    id: str


class Room:
    id: str
    participants: List[Session] = []


class RoomsManager:
    rooms: List[Room]

    def __init__(self):
        self.rooms = []

    def join(self, sid_participant: str, sid_room: str) -> None:
        participant = Session()
        participant.id = sid_participant

        filtered = [room for room in self.rooms if room.id == sid_room]
        if len(filtered) > 0:
            filtered[0].participants.append(participant)
        else:
            room = Room()
            room.id = sid_room
            room.participants.append(participant)

    def participants(self, sid_room) -> List[Session]:
        filtered = [room for room in self.rooms if room.id == sid_room]
        if len(filtered) > 0:
            return filtered[0].participants
        else:
            return []

