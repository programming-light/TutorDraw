import cv2
import numpy as np
import mss
import pyaudio
import wave
import os
import threading
import time
import subprocess
from datetime import datetime
import tempfile

class ScreenRecorder:
    def __init__(self, output_filename="output.mp4", fps=30, area=None, record_audio=True):
        self.output_filename = output_filename
        self.fps = fps
        self.area = area  # QRect object or None for full screen
        self.record_audio = record_audio
        
        self.is_recording = False
        self.is_paused = False
        self.frame_thread = None
        self.audio_thread = None
        
        self.video_writer = None
        self.audio_frames = []
        self.audio_stream = None
        self.p = None # PyAudio instance

        self.screen_capturer = mss.mss()

        self.audio_format = pyaudio.paInt16
        self.audio_channels = 2
        self.audio_rate = 44100
        self.audio_chunk = 1024 # Number of audio frames per buffer

        # FFmpeg executable path (assuming it's in PATH or specified)
        self.ffmpeg_path = "ffmpeg" 

    def start_recording(self):
        if self.is_recording:
            print("Already recording.")
            return

        self.is_recording = True
        self.is_paused = False
        self.video_frames_path = os.path.join(tempfile.gettempdir(), f"temp_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.avi")
        self.audio_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav")

        if self.area:
            monitor = {
                "top": self.area.y(),
                "left": self.area.x(),
                "width": self.area.width(),
                "height": self.area.height()
            }
            # Ensure dimensions are even for some video codecs
            monitor["width"] -= monitor["width"] % 2
            monitor["height"] -= monitor["height"] % 2
        else:
            monitor = self.screen_capturer.monitors[0] # Primary monitor

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'DIVX') # You can try 'mp4v' for .mp4, but 'DIVX' is widely supported for .avi
        self.video_writer = cv2.VideoWriter(self.video_frames_path, fourcc, self.fps, (monitor["width"], monitor["height"]))
        
        if not self.video_writer.isOpened():
            print(f"Error: Could not open video writer for {self.video_frames_path}")
            self.is_recording = False
            return

        self.frame_thread = threading.Thread(target=self._record_frames, args=(monitor,))
        self.frame_thread.start()

        if self.record_audio:
            self.p = pyaudio.PyAudio()
            self.audio_stream = self.p.open(format=self.audio_format,
                                            channels=self.audio_channels,
                                            rate=self.audio_rate,
                                            input=True,
                                            frames_per_buffer=self.audio_chunk)
            self.audio_frames = []
            self.audio_thread = threading.Thread(target=self._record_audio)
            self.audio_thread.start()
        
        print(f"Recording started to {self.output_filename}")

    def _record_frames(self, monitor):
        start_time = time.time()
        frames_captured = 0
        while self.is_recording:
            if not self.is_paused:
                img = self.screen_capturer.grab(monitor)
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR) # Convert to BGR for OpenCV
                self.video_writer.write(frame)
                frames_captured += 1
            # Control frame rate
            elapsed_time = time.time() - start_time
            expected_frames = int(elapsed_time * self.fps)
            if frames_captured > expected_frames:
                time.sleep(1 / self.fps) # Sleep to maintain FPS
        
        self.video_writer.release()
        print(f"Video capture thread stopped. Frames captured: {frames_captured}")

    def _record_audio(self):
        print("Audio capture thread started.")
        while self.is_recording:
            if not self.is_paused:
                try:
                    data = self.audio_stream.read(self.audio_chunk)
                    self.audio_frames.append(data)
                except Exception as e:
                    print(f"Error reading audio stream: {e}")
            else:
                time.sleep(0.1) # Sleep while paused
        
        # Save audio to WAV file
        if self.audio_frames:
            wf = wave.open(self.audio_path, 'wb')
            wf.setnchannels(self.audio_channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.audio_rate)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
            print(f"Audio saved to {self.audio_path}")

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.p.terminate()
        print("Audio capture thread stopped.")

    def pause_recording(self):
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            print("Recording paused.")

    def resume_recording(self):
        if self.is_recording and self.is_paused:
            self.is_paused = False
            print("Recording resumed.")

    def stop_recording(self):
        if not self.is_recording:
            print("Not recording.")
            return

        self.is_recording = False
        if self.frame_thread:
            self.frame_thread.join()
        if self.audio_thread:
            self.audio_thread.join()
        
        print("Recording stopped. Merging video and audio...")
        self._merge_video_audio()
        print(f"Final recording saved to {self.output_filename}")
        self._cleanup_temp_files()

    def _merge_video_audio(self):
        if self.record_audio and os.path.exists(self.audio_path):
            # Use FFmpeg to merge video and audio
            output_full_path = self.output_filename
            command = [
                self.ffmpeg_path,
                "-i", self.video_frames_path,
                "-i", self.audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                "-y", # Overwrite output file without asking
                output_full_path
            ]
            try:
                subprocess.run(command, check=True, capture_output=True)
                print(f"FFmpeg merged video and audio to {output_full_path}")
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error: {e.stderr.decode()}")
                print("Could not merge video and audio. Saving video only.")
                # Fallback to just saving the video file if merge fails
                os.rename(self.video_frames_path, output_full_path)
            except FileNotFoundError:
                print("FFmpeg executable not found. Please ensure FFmpeg is installed and in your system's PATH.")
                print("Saving video only.")
                os.rename(self.video_frames_path, output_full_path)
        else:
            # If no audio or audio recording failed, just rename the video file
            output_full_path = self.output_filename
            os.rename(self.video_frames_path, output_full_path)
            print(f"Video saved to {output_full_path} (no audio or audio merge skipped).")

    def _cleanup_temp_files(self):
        if os.path.exists(self.video_frames_path):
            os.remove(self.video_frames_path)
            print(f"Cleaned up temporary video file: {self.video_frames_path}")
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)
            print(f"Cleaned up temporary audio file: {self.audio_path}")

    def __del__(self):
        if self.is_recording:
            self.stop_recording()
