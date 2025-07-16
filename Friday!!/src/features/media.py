import os
import random
import pygame 
import pyautogui
import psutil
import time
import webbrowser
from src.core.voice import *
from AppOpener import open as open_app


class SpotifyPlayer:
    def __init__(self):
        self.initialized = False

    def is_spotify_running(self):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'spotify' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False

    def open_app(self):
        if self.initialized:
            return

        try:
            open_app("spotify")
            print("Trying to open Spotify app...")
        except Exception as e:
            print(f"Error launching Spotify app: {e}")
            return

        self.initialized = True

    def play(self):
        pyautogui.press("playpause")
        speak("Playing Spotify track")

    def pause(self):
        pyautogui.press("playpause")
        speak("Paused Spotify playback")

    def resume(self):
        pyautogui.press("playpause")
        speak("Resumed Spotify playback")

    def next_track(self):
        pyautogui.press("nexttrack")
        speak("Skipped to next Spotify track")

    def previous_track(self):
        pyautogui.press("prevtrack")
        speak("Went to previous Spotify track")


def handle_music(command):
    try:
        music_folder = "D:\\Security\\Phone\\Music"
        if not os.path.exists(music_folder):
            speak("Your Music folder was not found.")
            return

        music_files = [file for file in os.listdir(music_folder) if file.lower().endswith('.mp3')]

        if not music_files:
            speak("No music files found.")
            return

        def play_random():
            file_path = os.path.join(music_folder, random.choice(music_files))
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            speak(f"Playing {os.path.basename(file_path)}")

        if 'play' in command and 'change' not in command:
            play_random()
        elif 'pause' in command:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                speak("Music paused")
            else:
                speak("No music is currently playing")
        elif 'resume' in command:
            pygame.mixer.music.unpause()
            speak("Music resumed")
        elif 'stop' in command:
            pygame.mixer.music.stop()
            speak("Music stopped")
        elif 'change' in command or 'next' in command:
            pygame.mixer.music.stop()
            play_random()
        else:
            speak("Please specify play, pause, resume, stop or change.")
    except Exception as e:
        speak("Sorry, I encountered an error with the music operation")
        print(f"Media error: {e}")
