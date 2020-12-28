import base64
import json
import os
import sys

from flask import Flask
from flask_socketio import SocketIO, emit

from app.base.application import ModelEngine
from app.features.emotions import FaceEmotionRecognitionModel

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.debug = False

io = SocketIO(app, cors_allowed_origins="*")
engine = ModelEngine()


@io.on("frame")
def handle_frame(payload):
    if not isinstance(payload, dict):
        return

    token = payload.get("token")
    frame_string = payload.get("frame")

    frame = None

    try:
        frame = frame_string.split(',')[1]
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
