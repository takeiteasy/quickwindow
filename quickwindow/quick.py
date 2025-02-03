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

from .window import *
from typing import Optional, Union, Tuple, Dict
from contextlib import contextmanager

class QuickWindow(ManagedWindow, FrameLimiter):
    def __init__(self, width: int, height: int, title: str, limit: Optional[Union[int, float]] = None, **kwargs):
        ManagedWindow.__init__(self, width, height, title, **kwargs)
        FrameLimiter.__init__(self, limit)

    def loop(self):
        while not self.should_close:
            self.poll_events()
            yield self.limit()
            self.swap_buffers()

__window__ = None

def get_quick_window():
    return __window__

@contextmanager
def quick_window(width: Optional[int] = 640,
                 height: Optional[int] = 480,
                 title: Optional[str] = "quickwindow",
                 frame_limit: Optional[Union[int, str]] = None,
                 versions: Optional[Tuple[int, int, bool]] = None,
                 monitor: Optional[Monitor] = None,
                 shared: Optional[Window] = None,
                 hints: Optional[Dict] = None):
    global __window__
    if __window__ is not None:
        raise RuntimeError("Can only have 1 instance of quick_window()")
    init_glfw()
    if not versions:
        versions = (3, 3, True), (3, 2, True), (3, 1, False), (3, 0, False)
    else:
        if not isinstance(versions, list):
            versions = [versions]
    for vermaj, vermin, iscore in versions:
        try:
            Window.hint()
            Window.hint(context_version=(vermaj, vermin))
            if iscore:
                Window.hint(forward_compat=True)
                Window.hint(opengl_profile=Window.CORE_PROFILE)
            break
        except (api.PlatformError, api.VersionUnavailableError, ValueError) as e:
            iscore_str = 'CORE' if iscore else ''
            print("%s.%s %s: %s" % (vermaj, vermin, iscore_str, e))
    else:
        raise SystemExit("Proper OpenGL 3.x context not found")
    __window__ = QuickWindow(width, height, title, frame_limit, monitor=monitor, shared=shared, hints=hints, callbacks=None)
    yield __window__
