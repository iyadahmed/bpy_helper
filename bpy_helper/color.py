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
