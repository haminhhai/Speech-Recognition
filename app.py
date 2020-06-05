import tkinter as tk
from tkinter import W, S, N, E
from tkinter.filedialog import askopenfilename
import pyaudio
import wave
import os
import pickle
from train_model import get_mfcc


class App:
    def __init__(self, chunk=1024, sample_format=pyaudio.paInt16, channels=2, rate=44100, p=pyaudio.PyAudio()):
        # For recording
        self.CHUNK = chunk
        self.FORMAT = sample_format
        self.CHANNELS = channels
        self.RATE = rate
        self.p = p
        self.frames = []
        self.st = 1
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        self.recording = False

        # For model
        self.models = pickle.load(open("models_fixtransmat.pkl", "rb"))
        self.file_path = ""
        # self.predict = ""

        # For App
        self.main = tk.Tk()
        self.main.geometry('600x400')
        self.main.title('Speech Recognition')

        self.file_name = tk.Label(text="Choose test file")
        self.record_state = tk.Label(text="Record test file")
        self.result_text = tk.Label(text="Result: ")

        self.btn_select = tk.Button(self.main, text = "Select File", width = 30, height = 2, command=self.open_file, fg="black", bg="yellow")
        self.btn_record = tk.Button(self.main, text = "Start Record", width = 30, height = 2, command=self.record, fg="white", bg="purple")
        self.btn_predict = tk.Button(self.main, text = "Predict", width = 30, height = 3, command=self.predict, bg="red", fg="white")

        self.btn_select.grid(row=0, column=0, padx = 5, pady = 40)
        self.file_name.grid(row=0, column=1, sticky=W, padx = 20)
        self.btn_record.grid(row=2, column=0, padx = 5, pady = 40)
        self.record_state.grid(row=2, column=1, sticky=W, padx = 20 )
        self.btn_predict.grid(row=4, column=0, rowspan=2, pady = 55)
        self.result_text.grid(row=4, column=1, sticky=W, padx = 20, pady=50)
        self.main.mainloop()

    def start_record(self):
        self.result_text.config(text="Result: ")
        self.st = 1
        self.frames = []
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        print("start recording")
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            self.main.update()
        stream.close()
        wf = wave.open('test_record.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def stop_record(self):
        self.st = 0
        print("recording completed")

    def record(self):
        if self.recording == True:
            self.btn_record.config(text="Start Record")
            self.record_state.config(text="test_record.wav")
            self.recording = False
            self.stop_record()
            self.file_path = "test_record.wav"
        elif self.recording == False:
            self.btn_record.config(text="Stop Record")
            self.record_state.config(text="Recording ...")
            self.recording = True
            self.start_record()

    def open_file(self):
        """Predict from recorded file"""
        self.result_text.config(text="Result: ")
        self.file_path = askopenfilename(
            filetypes=[("WAV Files", "*.wav"), ("All Files", "*.*")])
        if not self.file_path:
            return
        print("File Selected")
        self.file_name.config(text=self.file_path.split('/')[-1])

    def predict(self):
        print("predicting")
        if not self.file_path:
            print("NO file")
            return
        O = get_mfcc(self.file_path)
        score = {cname : model.score(O, [len(O)]) for cname, model in self.models.items()}
        predict = max(score, key=score.get)
        print("predicted")
        self.result_text.config(text="Result: "+predict)


# Create an object of the ProgramGUI class to begin the program.
# main = tk.Tk()
# main.title('Speech Recognition')
# main.geometry('400x200')
app = App()
# main.mainloop()