# quickwindow

Python bindings for the GLFW library, fork of [pyglfw](https://github.com/pyglfw/pyglfw).

> [!NOTE]
> `pip install quickwindow==0.0.1`

```python
import quickwindow as qw

with qw.quick_window() as wnd:
    for dt in wnd.loop():
        for e in wnd.events():
            print(e)
        print(f"Δtime: {dt})")
```

> [!IMPORTANT]
> `libglfw3` dynamic library must be in path

```python
_lib = None
match platform.system():
    case "Windows":
        _lib = cdll.glfw3
    case "Darwin":
        _lib = cdll.LoadLibrary('libglfw.3.dylib')
    case _:
        _lib = cdll.LoadLibrary('libglfw.so.3')
```

## LICENSE
```
MIT License

Copyright (C) 2013 Roman Valov
Copyright (c) 2025 George Watson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
