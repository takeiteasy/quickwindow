# MIT License
# 
# Copyright (C) 2013 Roman Valov
# Copyright (c) 2025 George Watson
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass

__all__ = ["EventType", "KeyEvent", "CharEvent", "ScrollEvent", "MouseButtonEvent", "CursorEnterEvent", "CursorPosEvent", "WindowSizeEvent", "WindowPosEvent", "WindowCloseEvent", "WindowRefreshEvent", "WindowFocusEvent", "WindowIconifyEvent", "FrameBufferSizeEvent"]

class EventType:
    pass

@dataclass
class KeyEvent(EventType):
    key: int
    scancode: int
    action: int
    mods: int

@dataclass
class CharEvent(EventType):
    char: int

@dataclass
class ScrollEvent(EventType):
    dx: float
    dy: float

@dataclass
class MouseButtonEvent(EventType):
    button: int
    action: int
    mods: int

@dataclass
class CursorEnterEvent(EventType):
    status: bool

@dataclass
class CursorPosEvent(EventType):
    x: int
    y: int

@dataclass
class WindowSizeEvent(EventType):
    width: int
    height: int

@dataclass
class WindowPosEvent(EventType):
    x: int
    y: int

@dataclass
class WindowCloseEvent(EventType):
    pass

@dataclass
class WindowRefreshEvent(EventType):
    pass

@dataclass
class WindowFocusEvent(EventType):
    status: bool

@dataclass
class WindowIconifyEvent(EventType):
    status: bool

@dataclass
class FrameBufferSizeEvent(EventType):
    width: int
    height: int
