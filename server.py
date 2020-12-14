import sys
import base64

from flask import Flask
from flask_socketio import SocketIO

from app.base.application import ModelEngine
from app.features.emotions import FaceEmotionRecognitionModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

io = SocketIO(app, cors_allowed_origins="*")

engine = ModelEngine()


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
    else:
        print('Skipped frame...', file=sys.stdout)


if __name__ == 'server':
    engine.attach(FaceEmotionRecognitionModel())
    io.run(app)
