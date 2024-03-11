def add():
    global x, y
    x = (x + y) & 0xFFFFFFFF
    y = (x + y + 1) & 0xFFFFFFFF
    return x