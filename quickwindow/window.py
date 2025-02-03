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

from . import glfw as api
from .event import *
from threading import local
from typing import Optional, Union, Dict
import atexit
from queue import Queue

if bytes is str:
    _unichr = unichr
    _unistr = unicode
else:
    _unichr = chr
    _unistr = str

def _utf(obj):
    if bytes is not str:
        obj = obj.encode()
    return obj

def _str(obj):
    if bytes is not str:
        obj = obj.decode()
    return obj

class WindowType:
    pass

class _HintsBase:
    _hint_map_ = {
        'resizable':           api.GLFW_RESIZABLE,
        'visible':             api.GLFW_VISIBLE,
        'decorated':           api.GLFW_DECORATED,
        'red_bits':            api.GLFW_RED_BITS,
        'green_bits':          api.GLFW_GREEN_BITS,
        'blue_bits':           api.GLFW_BLUE_BITS,
        'alpha_bits':          api.GLFW_ALPHA_BITS,
        'depth_bits':          api.GLFW_DEPTH_BITS,
        'stencil_bits':        api.GLFW_STENCIL_BITS,
        'accum_red_bits':      api.GLFW_ACCUM_RED_BITS,
        'accum_green_bits':    api.GLFW_ACCUM_GREEN_BITS,
        'accum_blue_bits':     api.GLFW_ACCUM_BLUE_BITS,
        'accum_alpha_bits':    api.GLFW_ACCUM_ALPHA_BITS,
        'aux_buffers':         api.GLFW_AUX_BUFFERS,
        'samples':             api.GLFW_SAMPLES,
        'refresh_rate':        api.GLFW_REFRESH_RATE,
        'stereo':              api.GLFW_STEREO,
        'srgb_capable':        api.GLFW_SRGB_CAPABLE,
        'client_api':          api.GLFW_CLIENT_API,
        'context_ver_major':   api.GLFW_CONTEXT_VERSION_MAJOR,
        'context_ver_minor':   api.GLFW_CONTEXT_VERSION_MINOR,
        'context_robustness':  api.GLFW_CONTEXT_ROBUSTNESS,
        'debug_context':       api.GLFW_OPENGL_DEBUG_CONTEXT,
        'forward_compat':      api.GLFW_OPENGL_FORWARD_COMPAT,
        'opengl_profile':      api.GLFW_OPENGL_PROFILE,
    }

    _over_map_ = {
        'context_version':     (api.GLFW_CONTEXT_VERSION_MAJOR,
                                api.GLFW_CONTEXT_VERSION_MINOR,),

        'rgba_bits':           (api.GLFW_RED_BITS,
                                api.GLFW_GREEN_BITS,
                                api.GLFW_BLUE_BITS,
                                api.GLFW_ALPHA_BITS,),

        'rgba_accum_bits':     (api.GLFW_ACCUM_RED_BITS,
                                api.GLFW_ACCUM_GREEN_BITS,
                                api.GLFW_ACCUM_BLUE_BITS,
                                api.GLFW_ACCUM_ALPHA_BITS,),
    }

    def __init__(self, **kwargs):
        self._hints = {}

        for k, v in kwargs.items():
            is_hint = k in self.__class__._hint_map_
            is_over = k in self.__class__._over_map_
            if is_hint or is_over:
                setattr(self, k, v)

    def __getitem__(self, index):
        if index in self.__class__._hint_map_.values():
            return self._hints.get(index, None)
        else:
            raise TypeError()

    def __setitem__(self, index, value):
        if index in self.__class__._hint_map_.values():
            if value is None:
                if index in self._hints:
                    del self._hints[index]
            elif isinstance(value, int):
                self._hints[index] = value
        else:
            raise TypeError()

    def __delitem__(self, index):
        if index in self.__class__._hint_map_.values():
            if index in self._hints:
                del self._hints[index]
        else:
            raise TypeError()

def _hntprops_(hint_map, over_map):
    prop_map = {}

    def _hint_property(hint):
        def _get(self):
            return self[hint]

        def _set(self, value):
            self[hint] = value

        def _del(self):
            del self[hint]

        return property(_get, _set, _del)

    for prop, hint in hint_map.items():
        prop_map[prop] = _hint_property(hint)

    def _over_property(over):
        def _get(self):
            value = [self[hint] for hint in over]
            return tuple(value)

        def _set(self, value):
            for hint, v in zip(over, value):
                self[hint] = v

        def _del(self):
            for hint in over:
                del self[hint]

        return property(_get, _set, _del)

    for prop, over in over_map.items():
        prop_map[prop] = _over_property(over)

    return prop_map

Hints = type('Hints',
             (_HintsBase,),
             _hntprops_(_HintsBase._hint_map_, _HintsBase._over_map_))

class Mice:
    def __init__(self, handle):
        self.handle = handle
        self.ntotal = api.GLFW_MOUSE_BUTTON_LAST + 1

    def __len__(self):
        return (self.ntotal)

    def __getitem__(self, index):
        if isinstance(index, int):
            if (index < 0):
                index += self.ntotal
            elif (index >= self.ntotal):
                raise IndexError("Index %i is out of range" % index)

            return bool(api.glfwGetMouseButton(self.handle, index))
        elif isinstance(index, slice):
            return [self[i] for i in range(*index.indices(self.ntotal))]
        else:
            raise TypeError("Index %i is not supported" % index)

    LEFT = api.GLFW_MOUSE_BUTTON_LEFT

    @property
    def left(self):
        return self[api.GLFW_MOUSE_BUTTON_LEFT]

    RIGHT = api.GLFW_MOUSE_BUTTON_RIGHT

    @property
    def right(self):
        return self[api.GLFW_MOUSE_BUTTON_RIGHT]

    MIDDLE = api.GLFW_MOUSE_BUTTON_MIDDLE

    @property
    def middle(self):
        return self[api.GLFW_MOUSE_BUTTON_MIDDLE]

class _Keys:
    def __init__(self, handle):
        self.handle = handle

    def __getitem__(self, index):
        if isinstance(index, int):
            return bool(api.glfwGetKey(self.handle, index))

def _keyattrs_():
    _keyattribs_ = {}
    _key_prefix_ = 'GLFW_KEY_'
    _key_prelen_ = len(_key_prefix_)

    for name, item in vars(api).items():
        if name.startswith(_key_prefix_):
            _name_ = name[_key_prelen_:]
            if _name_[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                _name_ = 'NUM_' + _name_
            _name_ = _name_.upper()
            _prop_ = _name_.lower()

            _keyattribs_[_name_] = item
            if _prop_ == 'last' or _prop_ == 'unknown':
                continue
            _keyattribs_[_prop_] = property(lambda self, item=item: self[item])

    return _keyattribs_

Keys = type('Keys', (_Keys,), _keyattrs_())

class Joystick:
    def __init__(self, joyidx):
        self.joyidx = joyidx

    def __nonzero__(self):
        return bool(api.glfwJoystickPresent(self.joyidx))

    def __bool__(self):
        return bool(api.glfwJoystickPresent(self.joyidx))

    @property
    def name(self):
        return _str(api.glfwGetJoystickName(self.joyidx))

    @property
    def axes(self):
        return api.glfwGetJoystickAxes(self.joyidx)

    @property
    def buttons(self):
        return api.glfwGetJoystickButtons(self.joyidx)

def _monitor_obj(moni):
    monobj = super(Monitor, Monitor).__new__(Monitor)
    monobj.handle = moni.get_void_p()
    return monobj

class VideoMode:
    __slots__ = 'width', 'height', 'bits', 'refresh_rate'

    def __init__(self, vm):
        self.width = vm.width
        self.height = vm.height
        self.bits = (vm.redBits, vm.greenBits, vm.blueBits)
        self.refresh_rate = vm.refreshRate

class Monitor:
    _callback_ = None

    CONNECTED = api.GLFW_CONNECTED
    DISCONNECTED = api.GLFW_DISCONNECTED

    def __eq__(self, other):
        return self.handle.value == other.handle.value

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def set_callback(callback):
        if not callback:
            Monitor._callback_ = None
        else:
            def wrap(handle, *args, **kwargs):
                callback(_monitor_obj(handle), *args, **kwargs)
            Monitor._callback_ = api.GLFWmonitorfun(wrap)
        api.glfwSetMonitorCallback(Monitor._callback_)

    def __init__(self):
        raise TypeError("Objects of this class cannot be created")

    @property
    def pos(self):
        return api.glfwGetMonitorPos(self.handle)

    @property
    def name(self):
        return _str(api.glfwGetMonitorName(self.handle))

    @property
    def physical_size(self):
        return api.glfwGetMonitorPhysicalSize(self.handle)

    @property
    def video_mode(self):
        return VideoMode(api.glfwGetVideoMode(self.handle))

    @property
    def video_modes(self):
        return [VideoMode(vm) for vm in api.glfwGetVideoModes(self.handle)]

    def set_gamma(self, gamma):
        api.glfwSetGamma(self.handle, gamma)

    @property
    def gamma_ramp(self):
        return api.glfwGetGammaRamp(self.handle)

    @gamma_ramp.setter
    def gamma_ramp(self, rgb_ramp):
        api.glfwSetGammaRamp(self.handle, rgb_ramp)

    @staticmethod
    def all():
        return [_monitor_obj(moni) for moni in api.glfwGetMonitors()]

    @staticmethod
    def primary():
        return _monitor_obj(api.glfwGetPrimaryMonitor())

_glfw_initialized = False

def init_glfw():
    global _glfw_initialized
    if not _glfw_initialized:
        if not bool(api.glfwInit()):
            raise api.NotInitializedError()
        atexit.register(api.glfwTerminate)
        _glfw_initialized = True

class Window(WindowType):
    _instance_ = {}
    _contexts_ = local()

    def __init__(self, width: int, height: int, title: str,
                 monitor: Optional[Monitor] = None,
                 shared: Optional[WindowType] = None,
                 hints: Optional[Dict] = None,
                 callbacks: Optional[Dict] = None):
        if not _glfw_initialized:
            init_glfw()

        mon_handle = monitor and monitor.handle or None
        shr_handle = shared and shared.handle or None
        win_handle = api.glfwCreateWindow(width, height, _utf(title),
                                      mon_handle, shr_handle)

        self.handle = win_handle.get_void_p()
        self.__class__._instance_[self.handle.value] = self
        self.make_current()

        self.mice = Mice(self.handle)
        self.keys = Keys(self.handle)

        if hints:
            self.__class__.hint(hints=hints)

        if callbacks:
            self.set_callbacks(**callbacks)

    def __enter__(self):
        if not hasattr(Window._contexts_, 'ctxstack'):
            Window._contexts_.ctxstack = []
        Window._contexts_.ctxstack += [self.find_current()]

        api.glfwMakeContextCurrent(self.handle)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not Window._contexts_.ctxstack:
            raise RuntimeError('Corrupted context stack')

        _ctx = Window._contexts_.ctxstack.pop()
        api.glfwMakeContextCurrent(_ctx and _ctx.handle or _ctx)
        return False

    @classmethod
    def swap_current(cls, _ctx):
        if hasattr(Window._contexts_, 'ctxstack') and \
                Window._contexts_.ctxstack:
            raise RuntimeError('This function cannot be used inside `with`')
        api.glfwMakeContextCurrent(_ctx and _ctx.handle or _ctx)
        return _ctx

    def make_current(self):
        return self.swap_current(self)

    @classmethod
    def find_current(cls):
        find_handle = api.glfwGetCurrentContext().get_void_p()
        if bool(find_handle):
            return cls._instance_.get(find_handle.value)
        else:
            return None

    def close(self):
        api.glfwDestroyWindow(self.handle)

    @property
    def should_close(self):
        return bool(api.glfwWindowShouldClose(self.handle))

    @should_close.setter
    def should_close(self, flag):
        api.glfwSetWindowShouldClose(self.handle, flag)

    def swap_buffers(self):
        api.glfwSwapBuffers(self.handle)

    def swap_interval(self, interval):
        with self:
            api.glfwSwapInterval(interval)

    def set_title(self, title):
        api.glfwSetWindowTitle(self.handle, title)

    @property
    def framebuffer_size(self):
        return api.glfwGetFramebufferSize(self.handle)

    @property
    def pos(self):
        return api.glfwGetWindowPos(self.handle)

    @pos.setter
    def pos(self, x_y):
        api.glfwSetWindowPos(self.handle, *x_y)

    @property
    def size(self):
        return api.glfwGetWindowSize(self.handle)

    @size.setter
    def size(self, x_y):
        api.glfwSetWindowSize(self.handle, *x_y)

    def iconify(self):
        api.glfwIconifyWindow(self.handle)

    def restore(self):
        api.glfwRestoreWindow(self.handle)

    def _get_attrib(self, attrib):
        return api.glfwGetWindowAttrib(self.handle, attrib)

    @property
    def iconified(self):
        return bool(self.set_get_attrib(api.GLFW_ICONIFIED))

    @iconified.setter
    def iconified(self, flag):
        if flag:
            self.iconify()
        else:
            self.restore()

    def hide(self):
        api.glfwHideWindow(self.handle)

    def show(self):
        api.glfwShowWindow(self.handle)

    @property
    def visible(self):
        return bool(self.set_get_attrib(api.GLFW_VISIBLE))

    @visible.setter
    def visible(self, flag):
        if flag:
            self.show()
        else:
            self.hide()

    @property
    def has_focus(self):
        return bool(self.set_get_attrib(api.GLFW_FOCUSED))

    @property
    def resizable(self):
        return bool(self.set_get_attrib(api.GLFW_RESIZABLE))

    @property
    def decorated(self):
        return bool(self.set_get_attrib(api.GLFW_DECORATED))

    @property
    def context_version(self):
        return (self.set_get_attrib(api.GLFW_CONTEXT_VERSION_MAJOR),
                self.set_get_attrib(api.GLFW_CONTEXT_VERSION_MINOR),
                self.set_get_attrib(api.GLFW_CONTEXT_REVISION))

    @property
    def debug_context(self):
        return bool(self.set_get_attrib(api.GLFW_OPENGL_DEBUG_CONTEXT))

    @property
    def forward_compat(self):
        return bool(self.set_get_attrib(api.GLFW_OPENGL_FORWARD_COMPAT))

    OPENGL_API = api.GLFW_OPENGL_API
    OPENGL_ES_API = api.GLFW_OPENGL_ES_API

    @property
    def client_api(self):
        return self.set_get_attrib(api.GLFW_CLIENT_API)

    CORE_PROFILE = api.GLFW_OPENGL_CORE_PROFILE
    COMPAT_PROFILE = api.GLFW_OPENGL_COMPAT_PROFILE
    ANY_PROFILE = api.GLFW_OPENGL_ANY_PROFILE

    @property
    def opengl_profile(self):
        return self.set_get_attrib(api.GLFW_OPENGL_PROFILE)

    NO_ROBUSTNESS = api.GLFW_NO_ROBUSTNESS
    NO_RESET_NOTIFICATION = api.GLFW_NO_RESET_NOTIFICATION
    LOSE_CONTEXT_ON_RESET = api.GLFW_LOSE_CONTEXT_ON_RESET

    @property
    def context_robustness(self):
        return self.set_get_attrib(api.GLFW_CONTEXT_ROBUSTNESS)

    @staticmethod
    def hint(hints=None, **kwargs):
        if hints and kwargs:
            raise ValueError("Hints should be passed via object or via kwargs")

        if not hints:
            hints = Hints(**kwargs)

        if not hints._hints:
            api.glfwDefaultWindowHints()

        for hint, value in hints._hints.items():
            api.glfwWindowHint(hint, value)

    @property
    def monitor(self):
        moni = api.glfwGetWindowMonitor(self.handle)
        if bool(moni):
            return _monitor_obj(moni)
        else:
            return None

    @property
    def clipboard(self):
        return _str(api.glfwGetClipboardString(self.handle))

    @clipboard.setter
    def clipboard(self, buffer):
        api.glfwSetClipboardString(self.handler, _utf(buffer))

    _cursor_modes_get = {
        api.GLFW_CURSOR_DISABLED: None,
        api.GLFW_CURSOR_HIDDEN: False,
        api.GLFW_CURSOR_NORMAL: True,
    }

    _cursor_modes_set = {
        None: api.GLFW_CURSOR_DISABLED,
        False: api.GLFW_CURSOR_HIDDEN,
        True: api.GLFW_CURSOR_NORMAL,
    }

    @property
    def cursor_mode(self):
        libapi_cm = api.glfwGetInputMode(self.handle, api.GLFW_CURSOR)
        return self.set_cursor_modes_get.get(libapi_cm, None)

    @cursor_mode.setter
    def cursor_mode(self, mode):
        pyglfw_cm = self.set_cursor_modes_set.get(mode, None)
        api.glfwSetInputMode(self.handle, api.GLFW_CURSOR, pyglfw_cm)

    @property
    def sticky_keys(self):
        return bool(api.glfwGetInputMode(self.handle, api.GLFW_STICKY_KEYS))

    @sticky_keys.setter
    def sticky_keys(self, flag):
        api.glfwSetInputMode(self.handle, api.GLFW_STICKY_KEYS, flag)

    @property
    def sticky_mice(self):
        return bool(api.glfwGetInputMode(self.handle,
                                     api.GLFW_STICKY_MOUSE_BUTTONS))

    @sticky_mice.setter
    def sticky_mice(self, flag):
        api.glfwSetInputMode(self.handle, api.GLFW_STICKY_MOUSE_BUTTONS, flag)

    @property
    def cursor_pos(self):
        return api.glfwGetCursorPos(self.handle)

    @cursor_pos.setter
    def cursor_pos(self, x_y):
        api.glfwSetCursorPos(self.handle, *x_y)

    PRESS = api.GLFW_PRESS
    RELEASE = api.GLFW_RELEASE
    REPEAT = api.GLFW_REPEAT

    MOD_SHIFT = api.GLFW_MOD_SHIFT
    MOD_CONTROL = api.GLFW_MOD_CONTROL
    MOD_ALT = api.GLFW_MOD_ALT
    MOD_SUPER = api.GLFW_MOD_SUPER

    @classmethod
    def _wcb(cls, functype, func):
        if not func:
            return None

        def wrap(handle, *args, **kwargs):
            window = cls._instance_.get(handle.get_void_p().value, None)
            func(window, *args, **kwargs)
        return functype(wrap)

    def set_key_callback(self, callback):
        self.set_key_callback = self._wcb(api.GLFWkeyfun, callback)
        api.glfwSetKeyCallback(self.handle, self.set_key_callback)

    def set_char_callback(self, callback):
        def wrap(self, char):
            char = _unichr(char)
            callback(self, char)
        self.set_char_callback = self._wcb(api.GLFWcharfun, wrap)
        api.glfwSetCharCallback(self.handle, self.set_char_callback)

    def set_scroll_callback(self, callback):
        self.set_scroll_callback = self._wcb(api.GLFWscrollfun, callback)
        api.glfwSetScrollCallback(self.handle, self.set_scroll_callback)

    def set_cursor_enter_callback(self, callback):
        def wrap(self, flag):
            flag = bool(flag)
            callback(self, flag)
        self.set_cursor_enter_callback = self._wcb(api.GLFWcursorenterfun, wrap)
        api.glfwSetCursorEnterCallback(self.handle, self.set_cursor_enter_callback)

    def set_cursor_pos_callback(self, callback):
        self.set_cursor_pos_callback = self._wcb(api.GLFWcursorposfun, callback)
        api.glfwSetCursorPosCallback(self.handle, self.set_cursor_pos_callback)

    def set_mouse_button_callback(self, callback):
        self.set_mouse_button_callback = self._wcb(api.GLFWmousebuttonfun, callback)
        api.glfwSetMouseButtonCallback(self.handle, self.set_mouse_button_callback)

    def set_window_pos_callback(self, callback):
        self.set_window_pos_callback = self._wcb(api.GLFWwindowposfun, callback)
        api.glfwSetWindowPosCallback(self.handle, self.set_window_pos_callback)

    def set_window_size_callback(self, callback):
        self.set_window_size_callback = self._wcb(api.GLFWwindowsizefun, callback)
        api.glfwSetWindowSizeCallback(self.handle, self.set_window_size_callback)

    def set_window_close_callback(self, callback):
        self.set_window_close_callback = self._wcb(api.GLFWwindowclosefun, callback)
        api.glfwSetWindowCloseCallback(self.handle, self.set_window_close_callback)

    def set_window_refresh_callback(self, callback):
        self.set_window_refresh_callback = self._wcb(api.GLFWwindowrefreshfun, callback)
        api.glfwSetWindowRefreshCallback(self.handle, self.set_window_refresh_callback)

    def set_window_focus_callback(self, callback):
        def wrap(self, flag):
            flag = bool(flag)
            callback(self, flag)
        self.set_window_focus_callback = self._wcb(api.GLFWwindowfocusfun, wrap)
        api.glfwSetWindowFocusCallback(self.handle, self.set_window_focus_callback)

    def set_window_iconify_callback(self, callback):
        def wrap(self, flag):
            flag = bool(flag)
            callback(self, flag)
        self.set_window_iconify_callback = self._wcb(api.GLFWwindowiconifyfun, wrap)
        api.glfwSetWindowIconifyCallback(self.handle, self.set_window_iconify_callback)

    def set_framebuffer_size_callback(self, callback):
        self.set_framebuffer_size_callback = self._wcb(api.GLFWframebuffersizefun, callback)
        api.glfwSetFramebufferSizeCallback(self.handle, self.set_framebuffer_size_callback)

    def set_callbacks(self, **kwargs):
        callback_map = {
            'key': self.set_key_callback,
            'char': self.set_char_callback,
            'scroll': self.set_scroll_callback,
            'cursor_enter': self.set_cursor_enter_callback,
            'cursor_pos': self.set_cursor_pos_callback,
            'mouse_button': self.set_mouse_button_callback,
            'window_pos': self.set_window_pos_callback,
            'window_size': self.set_window_size_callback,
            'window_close': self.set_window_close_callback,
            'window_refresh': self.set_window_refresh_callback,
            'window_focus': self.set_window_focus_callback,
            'window_iconify': self.set_window_iconify_callback,
            'framebuffer_size': self.set_framebuffer_size_callback
        }
        for k, v in kwargs.items():
            if k in callback_map.keys():
                callback_map[k](v)
            else:
                raise ValueError(f"Invalid callback \"{k}\"")

    @staticmethod
    def api_version():
        return api.glfwGetVersion()

    @staticmethod
    def api_version_string():
        return _str(api.glfwGetVersionString())

    @staticmethod
    def poll_events():
        api.glfwPollEvents()

    @staticmethod
    def wait_events():
        api.glfwWaitEvents()

    def quit(self):
        self.should_close = True

class ManagedWindow(Window):
    def __init__(self, *args, **kwargs):
        if "callbacks" in kwargs.keys():
            del kwargs["callbacks"]
        super().__init__(*args, **kwargs)
        self.set_key_callback(ManagedWindow.key_callback)
        self.set_char_callback(ManagedWindow.char_callback)
        self.set_scroll_callback(ManagedWindow.scroll_callback)
        self.set_mouse_button_callback(ManagedWindow.mouse_button_callback)
        self.set_cursor_enter_callback(ManagedWindow.cursor_enter_callback)
        self.set_cursor_pos_callback(ManagedWindow.cursor_pos_callback)
        self.set_window_size_callback(ManagedWindow.window_size_callback)
        self.set_window_pos_callback(ManagedWindow.window_pos_callback)
        self.set_window_close_callback(ManagedWindow.window_close_callback)
        self.set_window_refresh_callback(ManagedWindow.window_refresh_callback)
        self.set_window_focus_callback(ManagedWindow.window_focus_callback)
        self.set_window_iconify_callback(ManagedWindow.window_iconify_callback)
        self.set_framebuffer_size_callback(ManagedWindow.framebuffer_size_callback)
        self._events = Queue()

    def events(self):
        while not self._events.empty():
            event = self._events.get()
            yield event

    def _clear_events(self):
        self._events = Queue()

    def __add_event(self, event: EventType):
        self._events.put(event)

    def key_callback(self, key, scancode, action, mods):
        self.__add_event(KeyEvent(key=key,
                                  scancode=scancode,
                                  action=action,
                                  mods=mods))

    def char_callback(self, char):
        self.__add_event(CharEvent(char=char))

    def scroll_callback(self, off_x, off_y):
        self.__add_event(ScrollEvent(dx=off_x,
                                     dy=off_y))

    def mouse_button_callback(self, button, action, mods):
        self.__add_event(MouseButtonEvent(button=button,
                                          action=action,
                                          mods=mods))

    def cursor_enter_callback(self, status):
        self.__add_event(CursorEnterEvent(status=status))

    def cursor_pos_callback(self, pos_x, pos_y):
        self.__add_event(CursorPosEvent(x=pos_x,
                                        y=pos_y))

    def window_size_callback(self, wsz_w, wsz_h):
        self.__add_event(WindowSizeEvent(width=wsz_w,
                                         height=wsz_h))

    def window_pos_callback(self, pos_x, pos_y):
        self.__add_event(WindowPosEvent(x=pos_x,
                                        y=pos_y))

    def window_close_callback(self):
        self.__add_event(WindowCloseEvent())

    def window_refresh_callback(self):
        self.__add_event(WindowRefreshEvent())

    def window_focus_callback(self, status):
        self.__add_event(WindowFocusEvent(status=status))

    def window_iconify_callback(self, status):
        self.__add_event(WindowIconifyEvent(status=status))

    def framebuffer_size_callback(self, fbs_x, fbs_y):
        self.__add_event(FrameBufferSizeEvent(width=fbs_x,
                                              height=fbs_y))

class FrameLimiter:
    def __init__(self, limit: Optional[Union[int, str]] = None):
        self._frame_limit = None
        self.set_frame_limit(limit)
        self.frame_prev_time = api.glfwGetTime()
        self.frame_current_time = self.frame_prev_time
        self.frame_count = 0
        self.frame_accum = 0

    @property
    def frame_limit(self):
        return self._frame_limit

    def set_frame_limit(self, limit: Optional[Union[str, int]]):
        self._frame_limit = limit
        self.frame_step = 0 if self._frame_limit is None else 1.0 / self._frame_limit

    def limit(self):
        self.frame_prev_time = self.frame_current_time
        self.frame_current_time = api.glfwGetTime()
        dt = self.frame_current_time - self.frame_prev_time
        if self.frame_limit is not None:
            self.frame_accum += dt
            self.frame_count += 1
            if self.frame_accum >= 1.0:
                self.frame_accum -= 1.0
                self.frame_count = 0
            while api.glfwGetTime() < self.frame_current_time + self.frame_step:
                pass
        return dt

