import base64
import json
import os
import sys

from flask import Flask
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room, emit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

from app.base.application import ModelEngine
from app.features.emotions import FaceEmotionRecognitionModel
from app.features.rooms import RoomsManager
from app.settings import DATABASE

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.debug = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
io = SocketIO(app, cors_allowed_origins="*")
engine = ModelEngine()


class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String())
    participants = db.Column(postgresql.JSONB)

    def __init__(self, code, participants):
        self.code = code
        self.participants = participants

    def __repr__(self):
        return f"<Room {self.code}>"


rooms = RoomsManager(Room, db)


@io.on("join")
def handle_join(payload):
    token = payload.get("token")
    room = payload.get("room")
    log('Received request to create or join room ' + payload.get("room"))

    participants = len(rooms.participants(room))
    log('Room ' + room + ' now has ' + str(participants) + ' client(s)')

    if participants == 0:
        join_room(room)
        rooms.join(token, room)
        log('Client ID ' + str(token) + ' created room ' + room)
        emit("created", room)
    elif participants == 1:
        log('Client ID ' + str(token) + ' joined room ' + room)
        join_room(room)
        rooms.join(token, room)
        emit('joined', room)
        emit('join', room, room=room, include_self=False)
    else:
        emit('full', room)


def log(*args):
    array = ['Message from server:']
    array.extend(args)
    emit('log', array)


@io.on("message")
def handle_message(payload):
    token = payload.get("token", None)
    room = rooms.get_room(token)
    log('message to room: ', room)
    if room is not None:
        message = payload.get("message", None)
        log('Client said: ', message)
        emit('message', message, room=room)


@io.on("frame")
def handle_frame(payload):
    if not isinstance(payload, str):
        return

    frame = None

    try:
        frame = payload.split(',')[1]
    except IndexError:
        pass

    if frame is not None:
        image = base64.b64decode(frame)
        engine.process(image)
        emit("results", json.dumps([result.__dict__ for result in engine.results()]))
    else:
        print('Skipped frame...', file=sys.stdout)


if __name__ == 'server':
    engine.attach(FaceEmotionRecognitionModel())

if __name__ == '__main__':
    io.run(app, host='0.0.0.0')
