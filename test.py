import quickwindow as qw

with qw.quick_window() as wnd:
    for dt in qw.loop():
        for e in qw.events():
            print(e)
        print(f"Δtime: {dt})")
