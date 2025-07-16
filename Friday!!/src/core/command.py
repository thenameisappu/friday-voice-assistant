import os
import webbrowser
import subprocess
import shutil
import logging
import pyautogui
import time
import keyboard
import psutil
import logging
import spotify
from datetime import datetime, timedelta
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from src.core.animation import *
from src.core.voice import get_text_command,listen_command,speak
from src.features.system import WindowsRadioControl, SystemMonitor ,adjust_brightness,adjust_volume
from src.features.timer import Timer, Stopwatch
from src.features.files import search_and_open_file,handle_file_operation
from src.features.media import handle_music,SpotifyPlayer
from src.features.notes import handle_note_operations
from src.features.weather import WeatherService
from src.features.application import open_app,close_app
from src.features.whatsapp import send_message_whatsapp_app
from src.utils.screen_utils import take_screenshot, record_screen
from src.utils import wifi_utils

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def execute_command(command):
    if not command:
        return True

    command = command.lower().strip()
    radio_control = WindowsRadioControl()
    spotify_player = SpotifyPlayer()
    system_monitor = SystemMonitor()
    timer = Timer()
    stopwatch = Stopwatch()
    weather_service = WeatherService()


    try:
        if any(word in command for word in ['search file', 'copy file', 'move file', 'delete file']):
            handle_file_operation(command)
        elif 'open file' in command:
            speak("What file would you like to open?")
            query = listen_command() or get_text_command()
            if query:
                search_and_open_file(query)

        elif any(word in command for word in ['play music', 'pause music', 'resume music', 'stop music']) or 'change music' in command or 'next song' in command:
            handle_music(command)

        elif 'calculate' in command:
            speak("What would you like to calculate?")
            expression = listen_command() or get_text_command()
            if expression:
                try:
                    result = eval(expression)
                    speak(f"The result is {result}")
                except:
                    speak("Sorry, I couldn't calculate that expression")

        elif 'note' in command or any(k in command for k in ['create note', 'add to note', 'read note', 'list notes', 'delete note']):
            handle_note_operations(command)

        elif 'start timer' in command:
            timer.start()
        elif 'stop timer' in command:
            timer.stop()
        elif 'start stopwatch' in command:
            stopwatch.start()
        elif 'stop stopwatch' in command:
            stopwatch.stop()
        elif 'reset stopwatch' in command:
            stopwatch.reset()

        elif 'what is your name' in command:
            speak("I am your Laptop assistant. You can call me Friday!")
        elif 'friday' in command:
            speak("I'm here")
        elif 'how are you' in command:
            speak("I'm doing great! Appreciate you asking.")

        elif 'weather' in command:
            speak("Which city would you like to know the weather for?")
            city = listen_command() or get_text_command()
            if city:
                weather = weather_service.get_current_weather(city)
                speak(f"Current weather in {city}: {weather['temperature']}°C, {weather['description']}, "
                      f"humidity {weather['humidity']}%, wind speed {weather['wind_speed']} meters per second")

        elif 'system status' in command:
            status = system_monitor.get_system_status()
            speak(f"CPU usage is currently {status['cpu']}%")
            memory = status['memory']
            speak(f"Memory status: Total {memory['total']} GB, "
                  f"Used {memory['used']} GB, "
                  f"Available {memory['available']} GB, "
                  f"Usage percentage {memory['percent']}%")

            for disk in status['disk']:
                speak(f"Disk {disk['device']} mounted at {disk['mountpoint']}: "
                      f"Total {disk['total']} GB, "
                      f"Used {disk['used']} GB, "
                      f"Free {disk['free']} GB, "
                      f"Usage percentage {disk['percent']}%")
            speak(f"This information was collected at {status['timestamp']}")
        elif 'cpu status' in command:
            cpu_usage = system_monitor.get_cpu_info()
            speak(f"Current CPU usage is {cpu_usage}%")
        elif 'memory status' in command:
            memory = system_monitor.get_memory_info()
            speak(f"Memory status: Total {memory['total']} GB, "
                  f"Used {memory['used']} GB, "
                  f"Available {memory['available']} GB, "
                  f"Usage percentage {memory['percent']}%")
        elif 'disk status' in command:
            disks = system_monitor.get_disk_info()
            for disk in disks:
                speak(f"Disk {disk['device']} mounted at {disk['mountpoint']}: "
                      f"Total {disk['total']} GB, "
                      f"Used {disk['used']} GB, "
                      f"Free {disk['free']} GB, "
                      f"Usage percentage {disk['percent']}%")

        elif 'wifi' in command:
            speak("Toggling WiFi")
            radio_control.wifi()
        elif 'bluetooth' in command:
            speak("Toggling Bluetooth")
            radio_control.bluetooth()
        elif 'hotspot' in command:
            speak("Toggling Mobile Hotspot")
            radio_control.hotspot()
        elif 'airplane mode' in command:
            speak("Toggling Airplane Mode")
            radio_control.airplane_mode()
        elif 'accessibility' in command:
            speak("Opening Accessibility Settings")
            radio_control.open_accessibility()
        elif 'projection' in command:
            speak("Opening Projection Menu")
            radio_control.open_projection()
        elif 'cast' in command:
            speak("Opening Cast Menu")
            radio_control.open_cast()

        elif 'connect' in command or 'connect to wifi' in command and 'with password' in command:
            try:
                networks = wifi_utils.list_wifi_networks()
                if networks:
                    speak("I found the following Wi-Fi networks nearby:")
                    for i, ssid in enumerate(networks, start=1):
                        speak(f"{i}. {ssid}")

                    speak("Please say the number of the Wi-Fi network you'd like to connect to.")
                    index_str = listen_command() or get_text_command()

                    try:
                        index = int(index_str) - 1
                        if 0 <= index < len(networks):
                            ssid = networks[index]
                            speak(f"You selected {ssid}. Please say the password.")
                            password = listen_command() or get_text_command()
                            speak(f"Trying to connect to {ssid}")
                            success = wifi_utils.connect_to_wifi(ssid, password)
                            if success:
                                speak(f"Connected to {ssid} successfully!")
                            else:
                                speak("Failed to connect, please check the password.")
                        else:
                            speak("Invalid selection.")
                    except ValueError:
                        speak("I didn't understand the number you said.")
                else:
                    speak("No Wi-Fi networks found.")
            except Exception as e:
                logging.error(f"Error connecting to Wi-Fi: {e}")
                speak("Sorry, I encountered an error while trying to connect to Wi-Fi.")


        elif 'find file' in command or 'find my file' in command:
            speak("What file are you looking for?")
            query = listen_command() or get_text_command()
            if query:
                search_and_open_file(query)

        elif 'open' in command:
            predefined_apps = {
                'notepad': 'notepad',
                'word': 'start winword',
                'excel': 'start excel',
                'powerpoint': 'start powerpnt',
                'outlook': 'start outlook'
                }
            for app, cmd in predefined_apps.items():
                if app in command:
                    speak(f"Opening {app.capitalize()}")
                    os.system(cmd)
                    return True
            
            if any(term in command for term in ['file', 'document', 'pdf', 'presentation', 'spreadsheet', 'image']):
                file_query = command.replace('open', '').strip()
                if file_query:
                    search_and_open_file(file_query)
                else:
                    speak("What file would you like to open?")
                    file_query = listen_command() or get_text_command()
                    if file_query:
                        search_and_open_file(file_query)
                return True

            elif 'browser' in command or 'youtube' in command:
                platform = 'YouTube' if 'youtube' in command else 'Google'
                speak(f"What would you like to search for on {platform}?")
                query = listen_command() or get_text_command()
                if query:
                    speak(f"Searching for {query}")
                    url = f'https://www.youtube.com/results?search_query={query}' if platform == 'YouTube' else f'https://www.google.com/search?q={query}'
                    webbrowser.open(url)
                return True

            elif "open" in command:
                app_name = command.replace("open", "").strip()
                if app_name:
                    open_app(app_name)
                else:
                    speak("Please specify the app to open.")
            
        elif 'close' in command:
            if 'window' in command:
                speak("Closing the current window")
                pyautogui.hotkey('alt', 'f4')
            elif 'recent' in command:
                speak("Closing the most recent window")
                pyautogui.hotkey('alt', 'tab')
                pyautogui.sleep(0.2)  
                pyautogui.hotkey('alt', 'f4')
            elif "close" in command:
                app_name = command.replace("close", "").strip()
                close_app(app_name)

        elif 'shutdown' in command:
            speak("Shutting down the system", is_exit=True)
            subprocess.run('shutdown /s /t 1', shell=True, check=True)
            return False
        elif 'restart' in command:
            speak("Restarting the system", is_exit=True)
            subprocess.run('shutdown /r /t 1', shell=True, check=True)
            return False
        elif 'lock' in command:
            speak("Locking the system")
            subprocess.run('rundll32.exe user32.dll,LockWorkStation', shell=True, check=True)
        elif 'hibernate' in command:
            speak("Hibernating the system")
            subprocess.run('shutdown /h', shell=True, check=True)
        elif 'sleep' in command:
            speak("Putting the system to sleep")
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True, check=True)

        elif 'volume' in command:
            speak("Would you like to increase or decrease the volume?")
            direction = listen_command() or get_text_command()
            if direction:
                adjust_volume(direction)

        elif 'brightness' in command:
            speak("Would you like to increase or decrease the brightness?")
            direction = listen_command() or get_text_command()
            if direction:
                adjust_brightness(direction)

        elif 'screenshot' in command or 'snapshot' in command:
            take_screenshot()
        elif 'record screen' in command or 'screen record' in command:
            speak("How many seconds should I record the screen for?")
            duration_str = listen_command() or get_text_command()
            try:
                duration = int(duration_str)
                record_screen(duration=duration)
            except ValueError:
                speak("Invalid duration. Please say a number of seconds.")
 
        elif 'time' in command:
            speak(f"The current time is {datetime.now().strftime('%I:%M %p')}")

        elif 'date' in command:
            speak(f"Today's date is {datetime.now().strftime('%B %d, %Y')}")

        elif 'battery' in command:
            battery = psutil.sensors_battery()
            if battery:
                speak(f"Battery is at {battery.percent}%. {'Plugged in' if battery.power_plugged else 'Not plugged in'}")
            else:
                speak("Battery information not available")
           
        elif 'delete' in command:
                speak("Which recording would you like to delete?")
                filename = listen_command() or get_text_command()
                if filename:
                    speak("Delete functionality is not yet implemented")
                else:
                    speak("Please specify what you would like to delete")            

        elif 'what can you do' in command:
            capabilities = [
                "open and close any applications",
                "adjust volume and brightness",
                "take screenshots",
                "get time and date",
                "check battery status",
                "control WiFi and Bluetooth",
                "manage hotspot and airplane mode",
                "open projection and cast menus",
                "shut down, restart, lock, hibernate",
                "close windows",
                "check weather",
                "monitor system status (CPU, memory, and disk usage)",
                "check individual CPU status",
                "check memory status",
                "check disk status",
                "start and control timer",
                "start, stop, and reset stopwatch",
                "play, pause, and change music",
                "search for files by name",
                "open any file on your computer",
                "copy, move, or delete files",
                "create and manage notes",
                "read, list, and delete notes",
                "search anything on the web",
                ]
            print("I can:")
            for capability in capabilities:
                speak(f"I can {capability}.")
        
        elif 'send message on whatsapp' in command or 'send' in command or 'send whatsapp message' in command or 'open whatsapp to send' in command:
            send_message_whatsapp_app()

        elif "play on spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.open_app()
            spotify_player.play()
        elif "pause spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.pause()
        elif "resume spotify" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.resume()
        elif "next spotify track" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.next_track()
        elif "previous spotify track" in command:
            spotify_player = SpotifyPlayer()
            spotify_player.previous_track()

        elif 'exit' in command or 'quit' in command:
            speak("Goodbye!", is_exit=True)
            return False

        else:
            speak("I didn't catch that. Can you please clarify?")
    except Exception as e:
        logging.error(f"Error executing command '{command}': {e}")
        speak("Sorry, I encountered an error executing that command")
        
    return True


