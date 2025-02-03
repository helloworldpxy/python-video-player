'''
python-video-player v0.8alpha
By HelloWorld05
一个简单的 Python 视频播放器，使用 OpenCV 和 Tkinter 实现。
'''
import tkinter as tk
from tkinter import filedialog, Scale
import cv2
from PIL import Image, ImageTk
import threading
import time

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Video Player")
        self.root.geometry("800x600")

        # 视频路径
        self.video_path = None
        self.cap = None
        self.total_frames = 0
        self.current_frame = 0
        self.playing = False
        self.playback_speed = 1.0  # 播放速度

        # GUI 组件
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(fill=tk.X, pady=10)

        self.btn_open = tk.Button(self.controls_frame, text="打开", command=self.open_video)
        self.btn_open.pack(side=tk.LEFT, padx=5)

        self.btn_play = tk.Button(self.controls_frame, text="播放", command=self.play_video)
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(self.controls_frame, text="暂停", command=self.pause_video)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(self.controls_frame, text="停止", command=self.stop_video)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.speed_scale = Scale(self.controls_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL, label="速度")
        self.speed_scale.set(1.0)
        self.speed_scale.pack(side=tk.LEFT, padx=10)

        self.seek_scale = Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, command=self.seek_video)
        self.seek_scale.pack(fill=tk.X, padx=10, pady=5)

        # 绑定事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_video(self):
        # 打开文件对话框选择视频
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv")])
        if not self.video_path:
            return

        # 打开视频
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print("错误：无法打开视频")
            return

        # 获取视频信息
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.seek_scale.config(to=self.total_frames)

        # 显示第一帧
        self.update_frame()

    def play_video(self):
        if not self.cap or not self.video_path:
            return

        self.playing = True
        threading.Thread(target=self._play_loop, daemon=True).start()

    def _play_loop(self):
        while self.playing and self.current_frame < self.total_frames:
            start_time = time.time()

            ret, frame = self.cap.read()
            if not ret:
                break

            self.current_frame += 1
            self.seek_scale.set(self.current_frame)

            # 显示帧
            self.display_frame(frame)

            # 控制播放速度
            delay = int((1 / (self.cap.get(cv2.CAP_PROP_FPS) * self.speed_scale.get())) * 1000)
            self.root.after(delay)

    def pause_video(self):
        self.playing = False

    def stop_video(self):
        self.playing = False
        self.current_frame = 0
        self.seek_scale.set(0)
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.update_frame()

    def seek_video(self, value):
        if not self.cap:
            return

        self.current_frame = int(value)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        self.update_frame()

    def update_frame(self):
        if not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            self.display_frame(frame)

    def display_frame(self, frame):
        # 将 OpenCV 帧转换为 PIL 图像
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=img)

        # 更新画布
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def on_close(self):
        self.playing = False
        if self.cap:
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    player = VideoPlayer(root)
    root.mainloop()