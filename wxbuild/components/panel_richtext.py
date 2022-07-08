from dataclasses import dataclass
import wx


def populate_sizer(content, direction: str = 'horizontal') -> tuple:  # TODO
    return (),


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    max_character: int = 50_000,