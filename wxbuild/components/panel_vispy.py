from dataclasses import dataclass
import wx
import vispy


def populate_sizer(content, direction: str = 'horizontal') -> tuple:  # TODO
    return (),


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_direction: str = 'horizontal'
    shape: tuple = (1, 1),
