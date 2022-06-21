import math

# https://easings.net/
def ease_in_sine(value: float):
    return 1 - math.cos((value * math.pi) / 2)


def ease_out_sine(value: float):
    return math.sin((value * math.pi) / 2)


def ease_in_out_sine(value: float):
    return -(math.cos(math.pi * value) - 1) / 2


def ease_in_cubic(value: float):
    return value * value * value


def ease_out_cubic(value: float):
    return 1 - (1 - value) ** 3


def ease_in_out_cubic(value: float):
    return 4 * value * value * value if value < 0.5 else 1 - ((2 - 2 * value) ** 3) / 2
