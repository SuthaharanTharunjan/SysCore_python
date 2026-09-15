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

_gradient_colour_cache={}
_bar_cache={}

bar_width = 15

def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def interpolate_color(color1, color2, amount,i):
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    r = round(r1 + (r2 - r1) * amount)
    g = round(g1 + (g2 - g1) * amount)
    b = round(b1 + (b2 - b1) * amount)

    _gradient_colour_cache[i]=(f"rgb({r},{g},{b})")


def gradient_color(i):
    position = i / (bar_width - 1)
    # position is between 0 and 1
    scaled = position * (len(GRADIENT) - 1)

    index = int(scaled)

    if index >= len(GRADIENT) - 1:
        _gradient_colour_cache[i]=GRADIENT[-1]
    else:
        amount = scaled - index
        interpolate_color(
            GRADIENT[index],
            GRADIENT[index + 1],
            amount,
            i
        )


def usage_details(usage, name=None):
    usage=round(usage)
    return _bar_cache[usage]

def _cache_creator():
    for i in range(bar_width):
        gradient_color(i)

def _bar_cache_creator():
    for i in range(0,101):
        filled = round((i / 100) * bar_width)
        
        text = Text()
        
        for p in range(bar_width):
            if p < filled:
                color = _gradient_colour_cache[p]
    
                text.append("▰", style=color)
            else:
                text.append("▰", style="grey35")
    
        text.append(f" {i:>3.0f}%")
    
        _bar_cache[i]=text

_cache_creator()
_bar_cache_creator()