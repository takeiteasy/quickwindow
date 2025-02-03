from quickwindow import quick_window, Keys, KeyEvent

with quick_window() as wnd:
    for dt in wnd.loop():
        for e in wnd.events():
            if isinstance(e, KeyEvent):
                if e.key == Keys.ESCAPE:
                    wnd.quit()
            print(e)
        print(f"Δtime: {dt})")
