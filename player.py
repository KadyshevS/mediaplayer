import customtkinter as ctk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from ffpyplayer.player import MediaPlayer
import time

class MediaPlayerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CustomTkinter Media Player")
        self.geometry("800x600")

        # Создаем фреймы
        self.video_frame = ctk.CTkFrame(self)
        self.video_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(padx=20, pady=20, fill="x")

        # Кнопки управления
        self.play_button = ctk.CTkButton(self.controls_frame, text="Play", command=self.play_media)
        self.play_button.pack(side="left", padx=10)

        self.pause_button = ctk.CTkButton(self.controls_frame, text="Pause", command=self.pause_media)
        self.pause_button.pack(side="left", padx=10)

        self.stop_button = ctk.CTkButton(self.controls_frame, text="Stop", command=self.stop_media)
        self.stop_button.pack(side="left", padx=10)

        self.open_button = ctk.CTkButton(self.controls_frame, text="Open", command=self.open_file)
        self.open_button.pack(side="left", padx=10)

        # Переменная для хранения пути к медиа файлу
        self.media_path = ""
        self.cap = None
        self.player = None
        self.playing = False
        self.paused = False
        self.current_frame_time = 0

        # Помещаем метку для отображения видео
        self.video_label = ctk.CTkLabel(self.video_frame)
        self.video_label.pack(fill="both", expand=True)

    def open_file(self):
        self.media_path = filedialog.askopenfilename(filetypes=[("Media Files", "*.mp4 *.mp3")])
        if self.media_path:
            self.play_media()

    def play_media(self):
        if self.media_path:
            if self.media_path.endswith(".mp4"):
                self.play_video(self.media_path)
            elif self.media_path.endswith(".mp3"):
                self.play_audio(self.media_path)

    def play_video(self, video_path):
        if not self.paused:
            self.cap = cv2.VideoCapture(video_path)
            self.player = MediaPlayer(video_path)
            self.playing = True
            self.update_frame()
        else:
            self.paused = False
            self.player.set_pause(False)
            self.cap.set(cv2.CAP_PROP_POS_MSEC, self.current_frame_time)
            self.update_frame()

    def update_frame(self):
        if self.playing and not self.paused and self.cap.isOpened():
            start_time = time.time()
            ret, frame = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            audio_frame, val = self.player.get_frame()

            if val == 'eof' or not ret:
                self.stop_media()
                return

            elapsed_time = time.time() - start_time
            delay = max(1, int((1/30 - elapsed_time) * 1000))  # Целевой FPS 30 кадров в секунду
            self.after(delay, self.update_frame)
        elif self.paused:
            # Если воспроизведение на паузе, сохраняем текущее время кадра
            self.current_frame_time = self.cap.get(cv2.CAP_PROP_POS_MSEC)

    def play_audio(self, audio_path):
        self.player = MediaPlayer(audio_path)
        self.player.set_pause(False)

    def pause_media(self):
        if self.player:
            self.paused = True
            self.player.set_pause(True)
            self.current_frame_time = self.cap.get(cv2.CAP_PROP_POS_MSEC)

    def stop_media(self):
        self.playing = False
        self.paused = False
        self.current_frame_time = 0
        if self.cap:
            self.cap.release()
        if self.player:
            self.player.close_player()
        self.video_label.configure(image=None)