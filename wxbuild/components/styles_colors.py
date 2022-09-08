import wx
# from wx import Colour
from dataclasses import dataclass

# from wxbuild.components.styles import Styles
from wxbuild.components.styles import Colors


@dataclass
class ColorScheme:  # TODO
    name: str = 'green'
    states: int = 1


@dataclass
class ColorsCyclic:
    cycler: tuple = (
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    )
    iterator: int = 0

    @classmethod
    def get_color(cls) -> str:
        color = cls.cycler[cls.iterator]
        cls.iterator = (cls.iterator + 1) % len(cls.cycler)
        return color

    @classmethod
    def get_color_by_index(cls, i: int) -> str:
        i = i % len(cls.cycler)
        return cls.cycler[i]


def get_colors_from_style(style):
    color_tuple = Colors[style]
    return [wx.Colour(color_str) for color_str in color_tuple]
