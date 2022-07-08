from dataclasses import dataclass
import wx
import wxbuild.components.custom_widgets.gradientbutton as wxGB


def populate_static_box(parent, mainframe, content, direction: str = 'horizontal') -> object:  # TODO
    return


def populate_sizer(parent, content, direction: str = 'horizontal') -> object:  # TODO
    # print(" populating sizer:: ", parent, mainframe)
    sizer_direction = (wx.HORIZONTAL, wx.VERTICAL)[direction != 'horizontal']
    print(" sizer_direction::", sizer_direction, wx.HORIZONTAL, wx.VERTICAL)
    sizer = wx.BoxSizer(sizer_direction)

    for i, element in enumerate(content):
        if isinstance(element, Spacer):
            sizer.AddSpacer(element.space)
        else:
            wx_element = WxWidget(widget=element, parent=parent)
            sizer.Add(wx_element.wx_object, 0, wx.ALL|wx.ALIGN_CENTER, 0)
            if element.end_space > 0:
                sizer.AddSpacer(element.end_space)

    return sizer


@dataclass(repr=False, eq=False, frozen=True)
class Spacer:
    space: int = 5


@dataclass(repr=False, eq=False, frozen=True)
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_direction: str = 'horizontal'
    content: tuple = ()


class PanelWithState(wx.Panel):
    def __init__(self, *args, **kwargs):
        self.main_frame = kwargs.pop('main_frame')
        self.panel_name = kwargs.pop('panel_name')
        content = kwargs.pop('content')
        print(" kwargs:: ", kwargs)
        super().__init__(*args, **kwargs)
        sizer = populate_sizer(self, content)
        self.SetSizerAndFit(sizer=sizer)


class WxWidget(object):
    def __init__(self, *args, **kwargs):  # TODO
        widget = kwargs.pop('widget')
        self.parent = kwargs.pop('parent')

        if 'input_' in widget.widget_type:
            self.wx_object = wx.StaticText(self.parent, -1, label=f'"error - couldnt create widget - {widget.label}"')
        else:
            if widget.widget_type == 'GradientButton':
                print("   gradient button: ", widget.size, widget.label)
                self.wx_object = wxGB.GradientButton(self.parent, id=-1, size=(-1,-1), label=widget.label)
            elif widget.widget_type == 'Button':
                self.wx_object = wx.StaticText(self.parent, -1, label=f'"error - couldnt create widget - {widget.label}"')
            elif widget.widget_type == 'static_text':
                self.wx_object = wx.StaticText(self.parent, -1, label=f'"error - couldnt create widget - {widget.label}"')
            elif widget.widget_type == 'choice':
                self.wx_object = wx.StaticText(self.parent, -1, label=f'"error - couldnt create widget - {widget.label}"')
            else:
                self.wx_object = wx.StaticText(self.parent, -1, label=f'"error - couldnt create widget - {widget.label}"')

    def set_label(self):  # TODO
        pass

    def get_label(self):  # TODO
        pass

    def set_value(self):  # TODO
        pass

    def get_value(self):  # TODO
        pass

    def set_color_text(self):  # TODO
        pass

    def set_color_bg(self):  # TODO
        pass

    def set_color_fg(self):  # TODO
        pass

    def set_choices(self):  # TODO
        pass


@dataclass
class ColorScheme:  # TODO
    name: str = 'green'
    states: int = 1


@dataclass
class TextScheme:  # TODO
    name: str = 'green'
    states: int = 1


#
# Attempt to make code more readable
@dataclass(init=False, repr=False, eq=False,frozen=True)
class Widgets:
    GradientButton = 'GradientButton'
    Button = 'Button'
    input_float_with_enable = 'input_float_with_enable'
    input_int_with_enable = 'input_int_with_enable'
    input_float = 'input_float'
    input_int = 'input_int'
    input_text = 'input_text'
    static_text = 'static_text'
    choice = 'choice'
    spacer = 'spacer'


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Schemes:
    green = 'green'
    red = 'red'
    blue = 'blue'
    cyan = 'cyan'
    toggle__on__off = 'toggle__on__off'
    c0 = 'c0'
    c1 = 'c1'
    c2 = 'c2'
    c3 = 'c3'
    c4 = 'c4'
    c5 = 'c5'



@dataclass
class Widget:
    widget_type: str
    parent: str = ""
    main_frame: str = ""
    #
    value: str | int | float | bool = ''
    label: str = ''
    choices: list | tuple = ()  # Should contain range of valid input numbers or choices for wx.Choice
    #
    value_edit_function: bool = False
    mouse_click_function: bool = False
    mouse_doubleclick_function: bool = False
    mouse_enter_function: bool = False
    mouse_leave_function: bool = False
    #
    theme_scheme_name: str = 'green'
    states: int = 1  # Number of states, color
    state: int = 0
    color_scheme: ColorScheme = ColorScheme(name = theme_scheme_name, states = states)
    text_scheme: TextScheme = TextScheme(name = theme_scheme_name, states = states)
    end_space: int = 5
    size: tuple[int, int] = (50, 40)

    def set_color_scheme(self, name: str):  # TODO
        self.color_scheme = ColorScheme(name)
