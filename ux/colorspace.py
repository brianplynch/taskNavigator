"""
Provides a color object that may be presented in various encodings
e.g. RGB, HSL, and HTML
"""

from __future__ import annotations


HUE_DESCRIPTORS = {
    "red" : 0,
    "orange" : 30,
    "yellow" : 60,
    "green" : 120,
    "cyan" : 180,
    "blue" : 240,
    "purple" : 300,        
}


SATURATION_DESCRIPTORS = {
    "gray": 0,
    "grayout": 25,
    "grayed": 50,
    "grayish": 75,
    "saturated": 100
}


LUMINOSITY_DESCRIPTORS = {
    "black": 0,
    "darkest": 10,
    "darker": 20,
    "dark": 30,
    "true": 50,
    "light": 70,
    "lighter": 80,
    "lightest": 90,
    "white": 100
}


def parse_color_description(description: str) -> ColorSpace:
    """
    hue_descriptors = red, orange, yellow, green, cyan, blue, purple
    
    saturation_descriptors = gray, grayout, grayed, grayish, saturated
    
    luminosity_descriptors = black, darkest, darker, dark, true, light, lighter, lightest, white
    """

    hue: int = 0 # red
    luminosity: int = 50 # true color
    saturation: int = 100 # saturated

    descriptors = description.split(sep = " ")
    # has a recognized hue
    has_hue = any(list(map(lambda d: d in HUE_DESCRIPTORS, descriptors)))
    if has_hue:
        recognized_hue = [descriptor for descriptor in descriptors if descriptor in HUE_DESCRIPTORS][0]
        hue = HUE_DESCRIPTORS[recognized_hue]

    # has a recognized saturation
    has_sat = any(list(map(lambda d: d in SATURATION_DESCRIPTORS, descriptors)))
    if has_sat:
        recognized_sat = [descriptor for descriptor in descriptors if descriptor in SATURATION_DESCRIPTORS][0]
        saturation = SATURATION_DESCRIPTORS[recognized_sat]

    # has a recognized luminosity
    has_lum = any(list(map(lambda d: d in LUMINOSITY_DESCRIPTORS, descriptors)))
    if has_lum:
        recognized_lum = [descriptor for descriptor in descriptors if descriptor in LUMINOSITY_DESCRIPTORS][0]
        luminosity = LUMINOSITY_DESCRIPTORS[recognized_lum]

    hsl = (hue, saturation, luminosity)
    return ColorSpace(hsl)


def hex_color(red: int, green: int, blue: int) -> str:
    """translates an rgb tuple of int to a tkinter friendly color code (HTML)"""
    rgb = red, green, blue
    if list(filter(lambda number: number>255 or number<0, rgb)):
        raise ValueError(f"{rgb} must be integers between 0 and 255")
    return "#%02x%02x%02x" % rgb 
    

def rgb_to_hsl(red: int, green: int, blue: int) -> tuple[int, int, int]:
    """returns a tuple of integers representing a hue-saturation-luminosity color (HSL)"""

    hue: int = 0
    luminosity: int = 0
    saturation: int = 0

    for color in (red, green, blue):
        if not 0 <= color <= 255:
            raise ValueError(f"{color=} must be integers from 0 to 255")
        
    red_percent = red / 255
    green_percent = green / 255
    blue_percent = blue / 255

    color_max = max(red_percent, green_percent, blue_percent)
    color_min = min(red_percent, green_percent, blue_percent)
    color_max_min_delta = color_max - color_min

    if color_max_min_delta > 0:
        hue_index = (red_percent, green_percent, blue_percent).index(color_max)
        parametric_hue = [
            int(60 * (((green_percent-blue_percent)/color_max_min_delta)%6)),
            int(60 * (((blue_percent-red_percent)/color_max_min_delta)+2)),
            int(60 * (((red_percent-green_percent)/color_max_min_delta)+4))
        ]
        hue = parametric_hue[hue_index]

    luminosity = int(100 * ((color_max + color_min) / 2))

    if color_max_min_delta > 0:
        saturation = int(100 * (color_max_min_delta / (1 - abs(2 * (luminosity / 100) - 1))))

    return (hue, saturation, luminosity)
    

def hsl_to_rgb(hue: int, saturation: int, luminosity: int) -> tuple[int, int, int]:
    """returns a tuple of integers representing a Red-Green-Blue color (RGB)"""

    if not 0 <= hue < 360:
        raise ValueError(f"{hue=}, must be an integer from 0 to 359")
    
    if not 0 <= saturation <= 100:
        raise ValueError(f"{saturation=}, must be an integer from 0 to 100")
    
    if not 0 <= luminosity <= 100:
        raise ValueError(f"{luminosity=}, must be an integer from 0 to 100")

    sat = saturation / 100
    lum = luminosity / 100

    c = (1 - abs(2 * lum - 1)) * sat
    x = c * (1 - abs(((hue / 60) % 2) - 1))
    m = lum - c / 2

    r_prime, g_prime, b_prime = [
        (c, x, 0),
        (x, c, 0),
        (0, c, x),
        (0, x, c),
        (x, 0, c),
        (c, 0, x)
    ][hue//60]

    red, green, blue = (int((r_prime + m)*255), int((g_prime + m)*255), int((b_prime + m)*255))

    return (red, green, blue)
    

def parse_hex_color(hex_color: str) -> ColorSpace:
    """translates a hex color code into an RGB tuple (R: int, G: int, B: int)"""
    value = hex_color.lstrip('#')
    value_length = len(value)
    red, green, blue = tuple(int(value[i:i + value_length // 3], 16) for i in range(0, value_length, value_length // 3))
    hsl = rgb_to_hsl(red, green, blue)
    return ColorSpace(hsl)


class ColorSpace:
    """A color object that represents a color by various encodings
    e.g. RGB, HSL, HTML/Hexidecimal
    """

    def __init__(self, hsl: tuple[int, int, int]) -> None:
        hue, saturation, luminosity = hsl

        if not 0 <= hue < 360:
            raise ValueError(f"{hue=}, must be an integer from 0 to 359")
        
        if not 0 <= saturation <= 100:
            raise ValueError(f"{saturation=}, must be an integer from 0 to 100")
        
        if not 0 <= luminosity <= 100:
            raise ValueError(f"{luminosity=}, must be an integer from 0 to 100")
        
        self.hue: int = hue
        self.saturation: int = saturation
        self.luminosity: int = luminosity
    
    @property
    def hsl(self) -> tuple[int, int, int]:
        return (self.hue, self.saturation, self.luminosity)

    @property
    def rgb(self) -> tuple[int, int, int]:
        return hsl_to_rgb(self.hue, self.saturation, self.luminosity)

    @property
    def hex(self) -> str:
        """translates an rgb tuple of int to a tkinter friendly color code (HTML)"""
        red, green, blue = self.rgb
        return hex_color(red, green, blue)
    
    @property
    def inverted_hsl(self) -> tuple[int, int, int]:
        """return a tuple of HSL as an inversion of the color"""
        rgb = self.rgb()
        irgb = tuple(map(lambda c: 255-c, rgb))
        hsl = rgb_to_hsl(*irgb)
        return hsl
    
    def invert(self) -> None:
        """invert the color"""
        rgb = self.rgb
        irgb = tuple(map(lambda c: 255-c, rgb))
        hue, saturation, luminosity = rgb_to_hsl(*irgb)
        self.hue = hue
        self.saturation = saturation
        self.luminosity = luminosity


if __name__ == "__main__":
    pass
