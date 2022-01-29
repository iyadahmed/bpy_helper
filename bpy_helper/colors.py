def hex_to_rgb(strColor):
    # supports '123456', '#123456' and '0x123456' and #123
    if len(strColor) == 4:
        strColor = '#{}'.format(''.join(2 * c for c in strColor.lstrip('#')))
    (r,g,b), a = map(lambda component: component / 255, bytes.fromhex(strColor[-6:])), 1.0
    return (round(r,4),round(g,4),round(b,4),a)