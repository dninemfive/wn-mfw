from typing import Self
from time import time_ns

def _fmt(start: int, end: int) -> str:
    return f'{(end - start) / 1e9:.3f}s'.rjust(9)

class Message(object):
    """ Wrapper for the {msg}...Done! pattern in a readable way """
    def __init__(self: Self, msg: str, indent: int = 0, padding: int = 0):
        self.msg = msg
        self.indent = indent
        self.has_nested = False
        self.start_time = time_ns()
        minlen = len(msg) + 3
        if padding < minlen:
            padding = minlen
        self.padding = padding
    
    def __enter__(self: Self):
        print(('  ' * self.indent) + self.msg.ljust(self.padding, "."), end="", flush=True)
        return self
    
    def __exit__(self: Self, exc_type, exc_value, traceback):
        report = ""
        if exc_type is not None or exc_value is not None or traceback is not None:
            report = f"Failed: {exc_type}"
        else:
            report = "Done!"
        print(f'{report} {_fmt(self.start_time, time_ns())}')

    def nest(self: Self, msg: str, padding: int = 0) -> Self:
        if not self.has_nested:
            print()
            self.has_nested = True
        return Message(msg, self.indent + 1, padding)