import cv2
import numpy as np
from keras.models import load_model
from keras.preprocessing.image import img_to_array

from app.base.abstract import IModel
from app.base.application import ResultProcess
from .config import RESOURCE_FACE_CLASSIFIER, RESOURCE_EMOTION_CLASSIFIER


class FaceEmotionRecognitionModel(IModel):
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier(RESOURCE_FACE_CLASSIFIER)
        self.emotion_classifier = load_model(RESOURCE_EMOTION_CLASSIFIER)
        self.labels = ['Enojad@', 'Feliz', 'Normal', 'Triste', 'Sorprendid@']

    def update(self, frame: bytes) -> ResultProcess:
        image = np.fromstring(frame, dtype=np.uint8)
        image = cv2.imdecode(image, 1)
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_coordinates = self.face_classifier.detectMultiScale(image_gray, 1.3, 5)

        for (x, y, w, h) in face_coordinates:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            face_gray = image_gray[y:y + h, x:x + w]
            face_gray = cv2.resize(face_gray, (48, 48), interpolation=cv2.INTER_AREA)

            if np.sum([face_gray]) != 0:
                face = face_gray.astype('float') / 255.0
                face = img_to_array(face)
                face = np.expand_dims(face, axis=0)

                prediction = self.emotion_classifier.predict(face)[0]
                result: ResultProcess = ResultProcess()
                result.model = __name__
                result.concept = self.labels[prediction.argmax()]
                return result
