from dataclasses import dataclass
import logging
logger = logging.getLogger('wx_log')

import wx
import wxbuild.components.custom_widgets.gradientbutton as wxgb
import wxbuild.components.custom_widgets.motorcontrol_rpmcurrent as wxmcrc
import wxbuild.components.custom_widgets.motorcontrol_drivestate as wxmds
import wxbuild.components.custom_widgets.motorcontrol_alarmstate as wxmas
import wxbuild.components.styles_colors as wxcolor
import wxbuild.components.styles_text as wxtext


#
# Basic widget class, all wx.widgets are declared/created here
class WxWidget:
    def __init__(self, **kwargs):  # TODO
        self.widget = kwargs.pop('widget')
        self.parent = kwargs.pop('parent')
        self.input_element = None

        self.state_key = f'state__{self.parent.panel_name}__{self.widget.name}'
        self.widget.set_text_scheme(self.widget.style_theme)
        self.widget.set_color_scheme(self.widget.style_theme)

        # If text control, this could contain enable button and input mask/filter
        if 'input_' in self.widget.widget_type:
            self.input_element = wx.TextCtrl(
                self.parent, -1, size=self.widget.size
            )
            if self.widget.value != '':
                self.input_element.SetValue(f'{self.widget.value}')

            if len(self.widget.label) > 0:
                self.wx_object = self.add_label_in_front_of_input_field(self.input_element, self.widget)
                if 'with_enable' in self.widget.widget_type:
                    bool_btn = wxgb.GradientButton(
                        self.parent, id=-1, size=(-1, 27), label='ON'
                    )
                    self.add_attributes_to_event_object(bool_btn)
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
                    self.add_attributes_to_event_object(bool_btn)
                    bool_btn.Bind(
                        event=wx.EVT_BUTTON,
                        handler=self.parent.main_frame.handle_user_event,
                    )
                    self.wx_object = wx.BoxSizer(wx.HORIZONTAL)
                    self.wx_object.Add(self.input_element, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 0)
                    self.wx_object.Add(bool_btn, 0, wx.RIGHT | wx.LEFT | wx.ALIGN_CENTER, 2)
                else:
                    self.wx_object = self.input_element

            self.add_attributes_to_event_object(self.input_element)
            # self.input_element.Bind(
            #     wx.EVT_CHAR,
            #     handler=self.parent.main_frame.input_state_edit,
            # )
            self.input_element.Bind(
                wx.EVT_TEXT,
                handler=self.parent.main_frame.input_state_edit,
            )
            # self.input_element.Bind(
            #     wx.EVT_TEXT_PASTE,
            #     handler=self.parent.main_frame.input_state_edit,
            # )
            # self.input_element.Bind(
            #     wx.EVT_TEXT_CUT,
            #     handler=self.parent.main_frame.input_state_edit,
            # )
            if self.widget.value_edit_function:
                self.input_element.Bind(
                    wx.EVT_CHAR,
                    handler=self.parent.main_frame.handle_user_event,
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
                if self.widget.font_size > 0:
                    current_font = self.wx_object.GetFont()
                    current_font.SetPointSize(self.widget.font_size)
                    self.wx_object.SetFont(current_font)
            elif self.widget.widget_type == 'choice':
                self.input_element = wx.Choice(
                    self.parent, -1, choices=self.widget.choices
                )
                if self.widget.value != '':
                    try:
                        self.input_element.SetSelection(self.widget.choices.index(self.widget.value))
                    except ValueError:
                        pass

                self.add_attributes_to_event_object(self.input_element)
                self.input_element.Bind(
                    wx.EVT_CHOICE,
                    handler=self.parent.main_frame.input_state_edit,
                )
                if self.widget.value_edit_function:
                    self.input_element.Bind(
                        wx.EVT_CHOICE,
                        handler=self.parent.main_frame.handle_user_event,
                    )

                if len(self.widget.label) > 0:
                    self.wx_object = self.add_label_in_front_of_input_field(self.input_element, self.widget)
                else:
                    self.wx_object = self.input_element
            elif self.widget.widget_type == 'MotorControlRpmCurrent':
                self.wx_object = wxmcrc.MotorControlRpmCurrent(
                    self.parent, -1, size=(-1, -1)
                )
            elif self.widget.widget_type == 'MotorControlAlarmState':
                self.wx_object = wxmas.MotorControlAlarmState(
                    self.parent, -1, size=(-1, -1)
                )
            elif self.widget.widget_type == 'MotorControlDriveState':
                self.wx_object = wxmds.MotorControlDriveState(
                    self.parent, -1, size=(-1, -1)
                )
            else:
                self.wx_object = wx.StaticText(
                    self.parent, -1, label=f'"error - couldnt create widget - {self.widget.label}"'
                )

        # Mouse events, connects to "handle_user_event"
        click_function_added = False
        if self.widget.mouse_click_function:
            if isinstance(self.wx_object, wx.Button) \
                    or isinstance(self.wx_object, wxgb.GradientButton) \
                    or isinstance(self.wx_object, wxmas.MotorControlAlarmState) \
                    or isinstance(self.wx_object, wxmds.MotorControlDriveState)\
                    or isinstance(self.wx_object, wxmcrc.MotorControlRpmCurrent):
                self.add_attributes_to_event_object(self.wx_object)
                self.wx_object.Bind(
                    event=wx.EVT_BUTTON,
                    handler=self.parent.main_frame.handle_user_event,
                )
                click_function_added = True
        if self.widget.mouse_rightclick_function:
            if isinstance(self.wx_object, wx.Button) or isinstance(self.wx_object, wxgb.GradientButton):
                self.wx_object.Bind(
                    event=wx.EVT_RIGHT_UP,
                    handler=self.parent.main_frame.handle_user_event,
                )
                if not click_function_added:
                    self.add_attributes_to_event_object(self.wx_object)
                    self.wx_object.Bind(
                        event=wx.EVT_BUTTON,
                        handler=self.parent.main_frame.handle_user_event,
                    )
                    click_function_added = True
        if self.widget.mouse_doubleclick_function:
            if not click_function_added:
                if isinstance(self.wx_object, wx.Button) or isinstance(self.wx_object, wxgb.GradientButton):
                    self.add_attributes_to_event_object(self.wx_object)
                    self.wx_object.Bind(
                        event=wx.EVT_BUTTON,
                        handler=self.parent.main_frame.handle_user_event,
                    )
        if self.widget.mouse_enter_function:
            self.add_attributes_to_event_object(self.wx_object)
            self.wx_object.Bind(
                event=wx.EVT_ENTER_WINDOW,
                handler=self.parent.main_frame.handle_user_event,
            )
        if self.widget.mouse_leave_function:
            self.add_attributes_to_event_object(self.wx_object)
            self.wx_object.Bind(
                event=wx.EVT_LEAVE_WINDOW,
                handler=self.parent.main_frame.handle_user_event,
            )

        self.set_style_of_self()
        self.update_value_from_state()

    @staticmethod
    def set_label(widget, text):  # TODO
        if isinstance(widget, wxgb.GradientButton):
            widget.SetLabel(text)

    @staticmethod
    def set_font(widget, font):
        if isinstance(widget, wxgb.GradientButton):
            widget.SetOwnFont(font)

    def get_label(self):  # TODO
        pass

    def set_value(self, value):
        if isinstance(self.input_element, wx.TextCtrl):
            self.input_element.SetValue(str(value))
        elif isinstance(self.input_element, wx.Choice):
            self.input_element.SetSelection(self.widget.choices.index(value))
        self.widget.value = value

    def get_value(self):
        return self.widget.value

    def set_value_by_event(self, value):
        if self.input_element is None:
            if isinstance(self.wx_object, wx.TextCtrl):
                self.widget.value = value
            elif isinstance(self.wx_object, wx.Choice):
                self.widget.value = self.wx_object.GetString(self.wx_object.GetCurrentSelection())
        else:
            if isinstance(self.input_element, wx.TextCtrl):
                self.widget.value = value
            elif isinstance(self.input_element, wx.Choice):
                self.widget.value = self.input_element.GetString(self.input_element.GetCurrentSelection())

    def update_value_from_state(self):
        if self.state_key in self.parent.main_frame.state:
            self.set_value(self.parent.main_frame.state[self.state_key])

    def set_color_text(self):  # TODO
        pass

    def set_color_bg(self):  # TODO
        pass

    def set_color_fg(self):  # TODO
        pass

    def set_choices(self):  # TODO
        pass

    def add_attributes_to_event_object(self, event_object):
        setattr(event_object, 'wx_widget', self)
        if not isinstance(event_object, wx.Sizer):
            setattr(self.parent.main_frame, self.state_key, event_object)

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

    def set_style_of_widget(self, widget, style=None):
        if style is None:
            style = self.widget.style_theme
        # logger.info(" -----> ", self.widget.name, self.widget.color_scheme, self.widget.text_scheme, self.widget.style_theme, type(widget))
        if isinstance(widget, wxgb.GradientButton):
            color_arr = wxcolor.get_colors_from_style(style)
            # color_arr = wxcolor.get_colors_from_style(self.widget.style_theme)
            widget.SetBaseColours(
                startcolour=color_arr[0],
                foregroundcolour=color_arr[-1]
            )
        elif isinstance(widget, wx.Choice):
            logger.info("    ----> CHOICE")
        elif isinstance(widget, wx.Button):
            logger.info("    ----> BUTTON")
        elif isinstance(widget, wx.TextCtrl):
            logger.info("    ----> TEXTCTRL")
        elif isinstance(widget, wx.StaticText):
            logger.info("    ----> STATICTEXT")


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
    mouse_rightclick_function: bool = False
    mouse_doubleclick_function: bool = False
    mouse_enter_function: bool = False
    mouse_leave_function: bool = False
    #
    style_theme: str = 'black'
    state_map: str = ''
    states: int = 1  # Number of states, color
    state: int = 0
    color_scheme: wxcolor.ColorScheme = wxcolor.ColorScheme(name=style_theme, states=states)
    text_scheme: wxtext.TextScheme = wxtext.TextScheme(name=style_theme, states=states)
    end_space: int = 0
    size: tuple[int, int] = (-1, -1)
    font_size: int = -1
    #


    def set_color_scheme(self, name: str):  # TODO
        self.color_scheme = wxcolor.ColorScheme(name=name)

    def set_text_scheme(self, name: str):
        self.text_scheme = wxtext.TextScheme(name=name)


@dataclass(init=False, repr=False, eq=False, frozen=True)
class Widgets:
    """All supported widgets"""
    MotorCtrlRpmCurrent: str = 'MotorControlRpmCurrent'
    MotorControlAlarmState: str = 'MotorControlAlarmState'
    MotorControlDriveState: str = 'MotorControlDriveState'
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


@dataclass(repr=False, eq=False, frozen=True)
class Spacer:
    space: int = 5


def populate_sizer(parent, content, direction: str = 'horizontal') -> object:
    sizer_direction = (wx.HORIZONTAL, wx.VERTICAL)[direction != 'horizontal']
    sizer = wx.BoxSizer(sizer_direction)

    for i, element in enumerate(content):
        if isinstance(element, Spacer):
            sizer.AddSpacer(element.space)
        else:
            wx_element = WxWidget(widget=element, parent=parent)
            sizer.Add(wx_element.wx_object, 0, wx.ALL | wx.ALIGN_CENTER, 0)
            if element.end_space > 0:
                sizer.AddSpacer(element.end_space)

    return sizer
