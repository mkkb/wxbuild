from dataclasses import dataclass
import wx
import wxbuild.components.custom_widgets.gradientbutton as wxgb


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


class PanelWithState(wx.Panel):
    def __init__(self, *args, **kwargs):
        self.main_frame = kwargs.pop('main_frame')
        self.panel_name = kwargs.pop('panel_name')
        content = kwargs.pop('content')
        super().__init__(*args, **kwargs)
        sizer = self.populate_sizer(self, content)
        self.SetSizerAndFit(sizer=sizer)

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
                wx_element = WxWidget(widget=element, parent=parent)
                #
                # print(" wx_element:: ", wx_element)
                #
                sizer.Add(wx_element.wx_object, 0, wx.ALL | wx.ALIGN_CENTER, 0)
                if element.end_space > 0:
                    sizer.AddSpacer(element.end_space)

        return sizer


#
# Basic widget class, all wx.widgets are declared/created here
class WxWidget(object):
    def __init__(self, **kwargs):  # TODO
        self.widget = kwargs.pop('widget')
        self.parent = kwargs.pop('parent')

        if 'input_' in self.widget.widget_type:
            input_element = wx.TextCtrl(
                self.parent, -1, size=self.widget.size
            )
            if self.widget.value != '':
                input_element.SetValue(f'{self.widget.value}')

            if len(self.widget.label) > 0:
                self.wx_object = self.add_label_in_front_of_input_field(input_element, self.widget)
                if 'with_enable' in self.widget.widget_type:
                    bool_btn = wxgb.GradientButton(
                        self.parent, id=-1, size=(-1, 27), label='ON'
                    )
                    self.add_attributes_to_event_object(bool_btn, 'mouse_click_function')
                    bool_btn.Bind(
                        event=wx.EVT_BUTTON,
                        handler=self.parent.main_frame.handle_user_event,
                    )
                    self.wx_object.Add(bool_btn, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 2)
            else:
                if 'with_enable' in self.widget.widget_type:
                    bool_btn = wxgb.GradientButton(
                        self.parent, id=-1, size=(-1, 27), label='ON'
                    )
                    self.add_attributes_to_event_object(bool_btn, 'mouse_click_function')
                    bool_btn.Bind(
                        event=wx.EVT_BUTTON,
                        handler=self.parent.main_frame.handle_user_event,
                    )
                    self.wx_object = wx.BoxSizer(wx.HORIZONTAL)
                    self.wx_object.Add(input_element, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 0)
                    self.wx_object.Add(bool_btn, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 2)
                else:
                    self.wx_object = input_element

            self.add_attributes_to_event_object(input_element, 'mouse_enter_function')
            input_element.Bind(
                wx.EVT_CHAR,
                handler=self.parent.main_frame.input_state_edit,
            )

        else:
            if self.widget.widget_type == 'GradientButton':
                self.wx_object = wxgb.GradientButton(
                    self.parent, id=-1, size=self.widget.size, label=self.widget.label
                )
            elif self.widget.widget_type == 'Button':
                self.wx_object = wx.Button(
                    self.parent, -1, size=(-1, -1), label=self.widget.label
                )
            elif self.widget.widget_type == 'static_text':
                self.wx_object = wx.StaticText(
                    self.parent, -1, label=self.widget.label
                )
            elif self.widget.widget_type == 'choice':
                input_element = wx.Choice(
                    self.parent, -1, choices=self.widget.choices
                )
                if self.widget.value != '':
                    try:
                        input_element.SetSelection(self.widget.choices.index(self.widget.value))
                    except ValueError:
                        pass

                self.add_attributes_to_event_object(input_element, 'mouse_enter_function')
                input_element.Bind(
                    wx.EVT_CHOICE,
                    handler=self.parent.main_frame.input_state_edit,
                )
                if self.widget.value_edit_function:
                    input_element.Bind(
                        wx.EVT_CHOICE,
                        handler=self.parent.main_frame.handle_user_event,
                    )

                if len(self.widget.label) > 0:
                    self.wx_object = self.add_label_in_front_of_input_field(input_element, self.widget)
                else:
                    self.wx_object = input_element
            else:
                self.wx_object = wx.StaticText(
                    self.parent, -1, label=f'"error - couldnt create widget - {self.widget.label}"'
                )

        # Mouse events, connects to "handle_user_event"
        if self.widget.mouse_click_function:
            if isinstance(self.wx_object, wx.Button) or isinstance(self.wx_object, wxgb.GradientButton):
                self.add_attributes_to_event_object(self.wx_object, 'mouse_click_function')
                self.wx_object.Bind(
                    event=wx.EVT_BUTTON,
                    handler=self.parent.main_frame.handle_user_event,
                )
        if self.widget.mouse_doubleclick_function:
            if isinstance(self.wx_object, wx.Button) or isinstance(self.wx_object, wxgb.GradientButton):
                self.add_attributes_to_event_object(self.wx_object, 'mouse_doubleclick_function')
                self.wx_object.Bind(
                    event=wx.EVT_BUTTON,
                    handler=self.parent.main_frame.handle_user_event,
                )
        if self.widget.mouse_enter_function:
            self.add_attributes_to_event_object(self.wx_object, 'mouse_enter_function')
            self.wx_object.Bind(
                event=wx.EVT_ENTER_WINDOW,
                handler=self.parent.main_frame.handle_user_event,
            )
        if self.widget.mouse_leave_function:
            self.add_attributes_to_event_object(self.wx_object, 'mouse_leave_function')
            self.wx_object.Bind(
                event=wx.EVT_LEAVE_WINDOW,
                handler=self.parent.main_frame.handle_user_event,
            )

        self.set_style_of_self()

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

    def add_attributes_to_event_object(self, event_object, event_type):
        setattr(event_object, 'source_name', self.widget.name)
        setattr(event_object, 'source_parent', self.parent)
        setattr(event_object, 'event_type', event_type)
        setattr(event_object, 'panel_name', self.parent.panel_name)
        if not isinstance(event_object, wx.Sizer):
            widget_name = f'state__{self.parent.panel_name}__{self.widget.name}'
            setattr(self.parent.main_frame, widget_name, event_object)

    def add_label_in_front_of_input_field(self, wx_object, widget):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label_text = wx.StaticText(
            self.parent, -1, label=widget.label
        )
        sizer.Add(label_text, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 2)
        sizer.Add(wx_object, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 0)
        return sizer

    def set_style_of_self(self):
        if isinstance(self.wx_object, wx.Sizer):
            children = self.wx_object.GetChildren()
            for child in children:
                self.set_style_of_widget(child.GetWindow())
        else:
            self.set_style_of_widget(self.wx_object)

    def set_style_of_widget(self, widget):
        print(" -----> ", type(widget), self.widget.color_scheme, self.widget.text_scheme)
        if isinstance(widget, wx.TextCtrl):
            print(" -------> ")


#
# Attempt to make code more readable when creating panel layouts
@dataclass
class ColorScheme:  # TODO
    name: str = 'green'
    states: int = 1


@dataclass
class TextScheme:  # TODO
    name: str = 'green'
    states: int = 1


@dataclass
class Widget:
    widget_type: str
    parent: str = ""
    main_frame: str = ""
    #
    name: str = ""
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
    style_theme: str = 'green'
    states: int = 1  # Number of states, color
    state: int = 0
    color_scheme: ColorScheme = ColorScheme(name=style_theme, states=states)
    text_scheme: TextScheme = TextScheme(name=style_theme, states=states)
    end_space: int = 0
    size: tuple[int, int] = (-1, -1)

    def set_color_scheme(self, name: str):  # TODO
        self.color_scheme = ColorScheme(name)


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Widgets:
    """All supported widgets"""
    GradientButton: str = 'GradientButton'
    Button: str = 'Button'
    input_float_with_enable: str = 'input_float_with_enable'
    input_int_with_enable: str = 'input_int_with_enable'
    input_float: str = 'input_float'
    input_int: str = 'input_int'
    input_text: str = 'input_text'
    static_text: str = 'static_text'
    choice: str = 'choice'
    spacer: str = 'spacer'


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Styles:
    green = 'green'
    red = 'red'
    blue = 'blue'
    cyan = 'cyan'
    black = 'black'
    grey = 'grey'
    white = 'white'
    toggle__on__off = 'toggle__on__off'
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
