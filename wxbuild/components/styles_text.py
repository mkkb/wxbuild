from dataclasses import dataclass
from wx import Colour, Font

from wxbuild.components.styles import Styles


@dataclass
class TextScheme:  # TODO
    name: str = 'green'
    states: int = 1

