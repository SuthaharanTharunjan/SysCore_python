from rich.text import Text

'''
GRADIENT = [
    "#32B8C8",  # cyan
    "#42B8BE",
    "#52B7B3",
    "#63B5A6",
    "#74B298",
    "#86AE89",
    "#97A878",
    "#A6A166",
    "#B39955",
    "#BE8F49",
    "#C58243",
    "#C87640",
    "#C6653D",
    "#B94D3A",
    "#9E3435",  # deep red
]
'''
GRADIENT = [
    "#00BCD5",  # cyan
    "#00BECF",
    "#0EC0C2",
    "#26BEAA",
    "#40BB91",
    "#5FB778",
    "#82B35D",
    "#A1A940",
    "#BC981D",
    "#C98006",
    "#D26900",
    "#D55700",
    "#D24300",
    "#C42300",
    "#A80004",
]

def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def interpolate_color(color1, color2, amount):
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    r = round(r1 + (r2 - r1) * amount)
    g = round(g1 + (g2 - g1) * amount)
    b = round(b1 + (b2 - b1) * amount)

    return f"rgb({r},{g},{b})"


def gradient_color(position):
    # position is between 0 and 1
    scaled = position * (len(GRADIENT) - 1)

    index = int(scaled)

    if index >= len(GRADIENT) - 1:
        return GRADIENT[-1]

    amount = scaled - index

    return interpolate_color(
        GRADIENT[index],
        GRADIENT[index + 1],
        amount
    )


def usage_details(usage, name=None):
    bar_width = 15
    filled = round((usage / 100) * bar_width)

    text = Text()

    for i in range(bar_width):
        if i < filled:
            position = i / (bar_width - 1)
            color = gradient_color(position)

            text.append("▰", style=color)
        else:
            text.append("▰", style="grey35")

    text.append(f" {usage:>3.0f}%")

    return text