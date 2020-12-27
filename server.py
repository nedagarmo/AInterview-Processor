import os
import sys
import base64
import json

from flask import Flask, request
from flask_migrate import Migrate
from flask_socketio import SocketIO, join_room
from flask_sqlalchemy import SQLAlchemy

from app.base.application import ModelEngine
from app.features.emotions import FaceEmotionRecognitionModel
from app.features.rooms import RoomsManager
from app.settings import NAMESPACE, DATABASE

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
    participants = db.Column(db.JSON)

    def __init__(self, code, participants):
        self.code = code
        self.participants = participants

    def __repr__(self):
        return f"<Room {self.code}>"


rooms = RoomsManager(Room, db)


@io.on("join")
def handle_join(payload):
    print("Connection message: ", payload, file=sys.stdout)
    token = payload.get("token")
    room = payload.get("room")

    participants = len(rooms.participants(room))
    print("Participants:", rooms.participants(room), file=sys.stdout)
    if participants == 0:
        join_room(room)
        rooms.join(token, room)
        io.emit("created", room)
    elif participants == 1:
        join_room(room)
        io.emit('join', room)
        rooms.join(token, room)
        io.emit('joined', room)
        io.emit('ready', room=room)
    else:
        io.emit('full', room)


@io.on("message")
def handle_message(message):
    io.emit('message', message, broadcast=True)


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
        io.emit("results", json.dumps([result.__dict__ for result in engine.results()]))
    else:
        print('Skipped frame...', file=sys.stdout)


if __name__ == 'server':
    engine.attach(FaceEmotionRecognitionModel())

if __name__ == '__main__':
    io.run(app, host='0.0.0.0')
