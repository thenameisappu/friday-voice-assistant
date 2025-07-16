from AppOpener import open as open_app_opener, close as close_app_opener
from src.core.voice import speak
import contextlib
import io

@contextlib.contextmanager
def suppress_stdout():
    with contextlib.redirect_stdout(io.StringIO()):
        yield

def open_app(name):
    try:
        with suppress_stdout():
            open_app_opener(name, match_closest=True, throw_error=True)
        speak(f"Opened {name}")
    except Exception as e:
        speak(f"Sorry, couldn't open {name}. Error: {e}")

def close_app(name):
    try:
        with suppress_stdout():
            close_app_opener(name, match_closest=True, throw_error=True)
        speak(f"Closed {name}")
    except Exception as e:
        speak(f"Sorry, couldn't close {name}. Error: {e}")
