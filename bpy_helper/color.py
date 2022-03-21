def hex_to_rgb(color_str_hex: str):
    """Supports '123456', '#123456', '0x123456' and #123"""
    color_str_hex = color_str_hex.lstrip("#")
    l = len(color_str_hex)
    assert (l == 3) or (l == 6)
    if l == 3:
        color_str_hex = "".join(2 * c for c in color_str_hex)
    r, g, b = bytes.fromhex(color_str_hex)
    return (r, g, b)


def rgb_to_hex(color: tuple[int, int, int]):
    return "#" + bytes(color).hex()


def rgb_to_hsv(color: tuple[float, float, float]) -> tuple[float, float, float]:

    r, g, b = color

    maxc = max(r, g, b)
    minc = min(r, g, b)

    v = maxc

    if minc == maxc:
        return 0.0, 0.0, v

    s = (maxc - minc) / maxc
    rc = (maxc - r) / (maxc - minc)
    gc = (maxc - g) / (maxc - minc)
    bc = (maxc - b) / (maxc - minc)

    if r == maxc:
        h = bc - gc
    elif g == maxc:
        h = 2.0 + rc - bc
    else:
        h = 4.0 + gc - rc

    h = (h / 6.0) % 1.0

    return (h, s, v)


def hsv_to_rgb(color: tuple[float, float, float]) -> tuple[float, float, float]:

    h, s, v = color

    if s == 0.0:
        return v, v, v

    i = int(h * 6.0)

    f = (h * 6.0) - i

    v1 = v * (1.0 - s)
    v2 = v * (1.0 - s * f)
    v3 = v * (1.0 - s * (1.0 - f))

    i = i % 6

    if i == 0:
        return v, v3, v1

    elif i == 1:
        return v2, v, v1

    elif i == 2:
        return v1, v, v3

    elif i == 3:
        return v1, v2, v

    elif i == 4:
        return v3, v1, v

    else:
        return v, v1, v2
