import os
import sys
import base64
import json

from flask import Flask, request
from flask_socketio import SocketIO, join_room

from app.base.application import ModelEngine
from app.features.emotions import FaceEmotionRecognitionModel
from app.features.rooms import RoomsManager
from app.settings import NAMESPACE

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.debug = False

io = SocketIO(app, cors_allowed_origins="*")
engine = ModelEngine()
rooms = RoomsManager()


@io.on("join")
def handle_join(room):
    print("Connection message: ", room, file=sys.stdout)

    participants = len(rooms.participants(room))
    print("Participants:", rooms.participants(room), file=sys.stdout)
    if participants == 0:
        join_room(room)
        rooms.join(request.sid, room)
        io.emit("created", room)
    elif participants == 1:
        join_room(room)
        io.emit('join', room)
        rooms.join(request.sid, room)
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
    io.run(app)
