import tkinter as tk
from tkinter import ttk, filedialog
from ttkbootstrap import Style
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment, silence
from gtts import gTTS

def extract_audio(video_path):
    clip = mp.VideoFileClip(video_path)
    clip.audio.write_audiofile("temp.wav")
    return "temp.wav"

def get_audio_chunks(audio_path):
    audio = AudioSegment.from_wav(audio_path)
    silence_thresh = -36
    silent_ranges = silence.detect_silence(audio, min_silence_len=500, silence_thresh=silence_thresh)
    chunks = []
    prev_end = 0
    for start, end in silent_ranges:
        chunks.append((prev_end, start, audio[prev_end:start]))
        prev_end = end
    chunks.append((prev_end, len(audio), audio[prev_end:]))
    return chunks


def speech_to_text(audio_chunk):
    recognizer = sr.Recognizer()
    audio_chunk.export("temp_chunk.wav", format="wav")
    with sr.AudioFile("temp_chunk.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "[inaudible]"
        return text

def create_subtitle():
    video_path = filedialog.askopenfilename(title="Select video file")
    if video_path:
        audio_path = extract_audio(video_path)
        audio_chunks = get_audio_chunks(audio_path)
        subtitles = []
        for _, (_, _, chunk) in enumerate(audio_chunks):  # Ignore the start and end times
            text = speech_to_text(chunk)
            subtitles.append(text)
        with open("subtitle.txt", "w") as file:  # Save as a .txt file since this isn't a proper SRT anymore
            file.write('\n'.join(subtitles))


def text_to_speech(text, lang='en-us'):
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_filename = 'output.mp3'
    tts.save(audio_filename)
    return audio_filename

def convert_subtitle_to_speech():
    subtitle_path = filedialog.askopenfilename(title="Select subtitle file")
    if subtitle_path:
        with open(subtitle_path, 'r', encoding='utf-8') as file:
            subtitle_content = file.read()
        audio_filename = text_to_speech(subtitle_content)
        print(f'Audio saved as {audio_filename}')


# GUI
root = tk.Tk()
style = Style(theme="darkly")

root.title("Subtitle Creator")
root.geometry('300x200')

frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

btn_create = ttk.Button(frame, text="Create Subtitle", command=create_subtitle, style='TButton')
btn_create.pack(pady=5, padx=10, fill='x')

btn_speech = ttk.Button(frame, text="Convert Subtitle to Speech", command=convert_subtitle_to_speech, style='TButton')
btn_speech.pack(pady=5, padx=10, fill='x')

root.mainloop()