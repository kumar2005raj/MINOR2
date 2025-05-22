from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
import speech_recognition as sr
from pydub import AudioSegment
from transformers import pipeline
import os

app = Flask(__name__)
CORS(app)

# Load summarization pipeline (load once at startup)
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print(f"Error loading summarization model: {e}")
    summarizer = None

def audio_to_text(audio_path):
    """Converts an audio file to text."""
    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        wav_path = "temp_audio.wav"
        audio.export(wav_path, format="wav")
        r = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
        os.remove(wav_path)  # Clean up temporary file
        return text, None
    except sr.UnknownValueError:
        return None, "Could not understand audio"
    except sr.RequestError as e:
        return None, f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return None, f"An error occurred during transcription: {e}"

def summarize_text(text):
    """Summarizes the given text."""
    if summarizer is None:
        return None, "Summarization model not loaded."
    try:
        summary = summarizer(text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
        return summary, None
    except Exception as e:
        return None, f"An error occurred during summarization: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_audio():
    if 'audio_file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio_file']
    if audio_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    temp_audio_path = "uploaded_audio"
    try:
        audio_file.save(temp_audio_path)
        transcription, transcription_error = audio_to_text(temp_audio_path)
        os.remove(temp_audio_path)  # Clean up uploaded file

        if transcription_error:
            return jsonify({'error': f'Transcription failed: {transcription_error}'}), 500

        if transcription:
            summary, summary_error = summarize_text(transcription)
            if summary_error:
                return jsonify({'transcription': transcription, 'error': f'Summarization failed: {summary_error}'}), 500
            return jsonify({'summary': summary, 'transcription': transcription}), 200
        else:
            return jsonify({'error': 'Could not process the audio for transcription'}), 500

    except Exception as e:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return jsonify({'error': f'An unexpected error occurred: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
