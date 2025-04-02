from quickwindow import quick_window, loop

with quick_window():
    for dt, events in loop():
        print(f"Δtime: {dt}\nevents: {events}")
