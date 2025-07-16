from src.core import animation
from src.core import command
from src.core.voice import *
import os
import msvcrt

def main():
    animation.start_animation()
    speak("Hello, I am Friday. How can I assist you today?")
    
    while True:
        if msvcrt.kbhit():
            command_text = get_text_command()
        else:
            command_text = listen_command()
        
        if not command.execute_command(command_text):
            break

    animation.stop_animation()

if __name__ == "__main__":
    main()
