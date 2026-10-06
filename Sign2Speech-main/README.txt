Sign2Speech
===========

Overview
--------
Sign2Speech is a web application that converts Indian Sign Language (ISL) videos into translated text output in English, Hindi, or Tamil. It records or accepts a video, sends it to a backend model for prediction, and then displays the translated result and plays the word aloud using text-to-speech.

Project Structure
-----------------

Sign2Speech-main/
├── backend/
│   ├── app.py
│   ├── inference.py
│   ├── label_map_english.json
│   ├── label_map_hindi.json
│   ├── label_map_tamil.json
│   ├── ISL_INCLUDE_NEW.keras
│   ├── requirements.txt
│   ├── runtime.txt
│   └── uploads/
│
├── frontend/
│   ├── app.js
│   ├── index.html
│   ├── style.css
│   └── assets/
│
└── README.txt


How the app works
-----------------

1. Frontend captures input
   - The frontend page in frontend/index.html loads the UI.
   - The user can either:
     - record a video using the webcam, or
     - upload an existing video file.
   - The selected language is chosen from the dropdown before prediction.

2. Frontend sends video to backend
   - The JavaScript in frontend/app.js creates a multipart form request.
   - It sends the video file and selected language to the backend endpoint:
     POST /predict
   - The backend is running in backend/app.py.

3. Backend runs model inference
   - The backend receives the uploaded file.
   - It saves the video temporarily in the uploads folder.
   - Then it calls predict_video() from backend/inference.py.
   - The model uses MediaPipe Holistic landmarks from the video and runs them through the trained TensorFlow Keras model.
   - It predicts the class ID and picks the corresponding label from the selected label map JSON.

4. Result is returned to frontend
   - The backend returns JSON containing:
     - class_id
     - label
     - confidence
     - language
   - The frontend shows the predicted label in the result card.

5. TTS / spoken output
   - After prediction, the backend converts the predicted word into speech using the gTTS library.
   - It generates an MP3 file and returns an audio_url.
   - The frontend automatically plays the audio using the browser Audio API.
   - The result card also has a replay button to play the audio again.

6. Changing language after prediction
   - The app stores the last prediction data in the frontend state.
   - When the user changes the dropdown language after a prediction, the frontend fetches the corresponding translated label from the same class ID in the selected label map.
   - It then requests TTS audio for that translated label and updates the displayed text and audio in-place.
   - No re-prediction is needed.


Backend details
---------------

File: backend/app.py

Main endpoints:
- GET /
  Returns a simple health/landing message.

- GET /health
  Returns {"status": "healthy"}

- POST /predict
  Accepts:
  - file: video
  - language: english | hindi | tamil

  Flow:
  - validates language
  - saves uploaded file temporarily
  - runs model prediction using predict_video()
  - creates spoken audio for the predicted label
  - returns JSON result including audio_url

- GET /label-map/{language}
  Returns the JSON label map for the requested language.

- GET /speak
  Takes the text and language and generates TTS audio.

Important note:
- Files are removed after prediction finishes to keep the uploads folder clean.
- Generated TTS MP3 files are stored inside uploads/tts and served by FastAPI static file routing.


Inference details
-----------------

File: backend/inference.py

This file handles the actual model pipeline:
- reads the video file frame by frame
- extracts pose, left-hand, right-hand, and face landmark data using MediaPipe Holistic
- converts the landmarks into a fixed feature vector
- pads/truncates to the model input size
- feeds it into the trained TensorFlow model
- finds the class with the highest confidence
- reads the matching label from the selected language map

Supported languages:
- english
- hindi
- tamil

The label maps are stored in:
- label_map_english.json
- label_map_hindi.json
- label_map_tamil.json

Each JSON file maps class IDs (as strings) to the word/phrase in that language.


Frontend details
----------------

File: frontend/app.js

This file handles:
- webcam capture
- recording start/stop logic
- file upload logic
- backend request creation
- UI state updates
- error handling
- prediction display
- TTS audio playback
- language-switch translation without rerunning prediction

Key frontend concept:
- The last prediction result is stored in JavaScript state.
- When the user changes language, the app does not call the model again.
- Instead, it looks up the same class ID in the new language label map and plays the translated word.


How to run the project
----------------------

Backend
-------
Open a terminal in the backend folder and run:

cd "D:\Deepankar Sharma\Sign2Speech-main\Sign2Speech-main\backend"
C:/Users/govin/AppData/Local/Programs/Python/Python311/python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Then check:
http://localhost:8000/health

Frontend
--------
Open a second terminal in the frontend folder and run:

cd "D:\Deepankar Sharma\Sign2Speech-main\Sign2Speech-main\frontend"
C:/Users/govin/AppData/Local/Programs/Python/Python311/python.exe -m http.server 8080

Then open:
http://localhost:8080

Important:
- Backend must run on port 8000.
- Frontend must run on port 8080.


How to use the app
------------------
1. Pick the output language.
2. Record or upload a sign-language video.
3. Click Predict Sign.
4. The app shows the predicted sign and speaks the word aloud.
5. If needed, change the language dropdown to instantly switch the displayed word and spoken voice without rerunning prediction.


Dependencies
------------
The backend dependencies are listed in backend/requirements.txt.
Main packages include:
- TensorFlow
- MediaPipe
- OpenCV
- NumPy
- FastAPI
- Uvicorn
- gTTS


Notes
-----
- The backend model is loaded from ISL_INCLUDE_NEW.keras.
- This project is intended for local development and demonstration.
- For production deployment, you would normally add better error handling, logging, environment variables, and deployment configuration.


Thank you
---------
This project demonstrates a simple end-to-end ISL-to-text pipeline that converts input video into a predicted sign label, displays it in multiple languages, and speaks it aloud.
