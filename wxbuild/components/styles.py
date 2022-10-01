from dataclasses import dataclass


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Styles:
    green = 'green'
    light_green = 'light_green'
    dark_green = 'dark_green'
    darker_green = 'darker_green'
    olive_light = 'olive_light'
    #
    red = 'red'
    salmon_red = 'salmon_red'
    orange = 'orange'
    #
    blue = 'blue'
    light_blue = 'light_blue'
    lighter_blue = 'lighter_blue'
    dark_blue = 'dark_blue'
    darker_blue = 'darker_blue'
    cyan = 'cyan'
    #
    black = 'black'
    white = 'white'
    grey = 'grey'
    #
    ivory = 'ivory'
    #
    toggle__on__off = 'toggle__on__off'
    #
    c0 = 'c0'
    c1 = 'c1'
    c2 = 'c2'
    c3 = 'c3'
    c4 = 'c4'
    c5 = 'c5'
    c6 = 'c6'
    c7 = 'c7'
    c8 = 'c8'
    c9 = 'c9'


Colors = {field: ('#000000', '#ffffff') for field in Styles.__dict__ if field[:2] != '__'}
Colors.update({
    #        background shades, foreground
    'black': ('#000000', '#ffffff'),
    'white': ('#ffffff', '#000000'),
    #
    'green': ('#00ff00', '#000000'),
    'light_green': ('#b3ffb4', '#000000'),
    'dark_green': ('#00d41e', '#ffffff'),
    'darker_green': ('#00640e', '#ffffff'),
    'lime': ('#aaff32', '#000000'),
    'olive_light': ('#daff79', '#000000'),
    #
    'ivory': ('#fdffdb', '#000000'),
    #
    'blue': ('#0000ff', '#ffffff'),
    'light_blue': ('#c3f9ff', '#000000'),
    'lighter_blue': ('#f8feff', '#000000'),
    'dark_blue': ('#0065db', '#ffffff'),
    'darker_blue': ('#004494', '#ffffff'),
    'cyan': ('#89e3ff', '#000000'),
    #
    'red': ('#ff0000', '#000000'),
    'salmon_red': ('#ff7e80', '#000000'),
    'orange': ('#ff9419', '#000000'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
    # 'cyan': ('#000000', '#ffffff'),
})
