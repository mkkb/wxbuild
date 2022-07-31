from dataclasses import dataclass
import wx


# def populate_sizer(content, direction: str = 'horizontal') -> tuple:  # TODO
#     return (),


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_flags: int = wx.EXPAND | wx.ALL
    sizer_proportion: float = 0
    sizer_border: int = 0
    max_character: int = 50_000,

