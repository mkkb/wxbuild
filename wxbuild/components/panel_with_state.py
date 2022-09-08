from dataclasses import dataclass
import wx
import wxbuild.components.widget as wxw


@dataclass(repr=False, eq=False, frozen=True)
class Spacer:
    space: int = 5


@dataclass(repr=False, eq=False, frozen=True)
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_flags: int = wx.EXPAND | wx.ALL
    sizer_proportion: float = 0
    sizer_border: int = 0
    sizer_direction: str = 'horizontal'
    content: tuple = ()
    background_color: tuple = wx.WHITE


class PanelWithState(wx.Panel):
    def __init__(self, *args, **kwargs):
        self.dataclass = WxPanel
        self.main_frame = kwargs.pop('main_frame')
        self.panel_name = kwargs.pop('panel_name')
        content = kwargs.pop('content')
        super().__init__(*args, **kwargs)
        sizer = self.populate_sizer(self, content)
        self.SetSizerAndFit(sizer=sizer)

    def post_init(self):
        self.SetBackgroundColour(self.dataclass.background_color)

    # def populate_static_box(parent, mainframe, content, direction: str = 'horizontal') -> object:  # TODO
    #     return

    @staticmethod
    def populate_sizer(parent, content, direction: str = 'horizontal') -> object:
        sizer_direction = (wx.HORIZONTAL, wx.VERTICAL)[direction != 'horizontal']
        sizer = wx.BoxSizer(sizer_direction)

        for i, element in enumerate(content):
            if isinstance(element, Spacer):
                sizer.AddSpacer(element.space)
            else:
                wx_element = wxw.WxWidget(widget=element, parent=parent)
                sizer.Add(wx_element.wx_object, 0, wx.ALL | wx.ALIGN_CENTER, 0)
                if element.end_space > 0:
                    sizer.AddSpacer(element.end_space)

        return sizer
