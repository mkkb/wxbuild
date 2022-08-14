from wxbuild.components.mainframe import MainFrame, AppConfiguration, WxComponents

from wx import App


def main():
    app = App()

    app_config = AppConfiguration
    app_config.title = 'Pseudo Oscilloscope'
    app_config.monitor_resources = True

    frm = MainFrame(app_config=app_config)

    layout_tuple = (
        control_panel,
        vispy_panel,
        control_panel_all_widgets,
    )
    frm.populate_frame(layout_tuple)

    frm.Show()
    app.MainLoop()


other_ctrl_button_labels = ('FFT', 'Hilbert', 'SNR', 'Spectrogram')
control_panel = WxComponents.panel(
    parent='main_frame',
    name='controls',
    sizer_direction='horizontal',
    content=(
        WxComponents.spacer(15),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'channel_{i+1}',
                label=f'CH{i+1}',
                value=True,
                style_theme=WxComponents.styles.green,
                mouse_click_function=True,
                end_space=4,
                size=(40, 30),
            ) for i in range(4)
        ),
        WxComponents.spacer(50),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{other_ctrl_button_labels[i]}'.lower(),
                label=f'{other_ctrl_button_labels[i]}',
                value=not i % 5,
                style_theme=WxComponents.styles.cyan,
                mouse_click_function=True,
                end_space=4,
                size=(80, 30),
            ) for i in range(len(other_ctrl_button_labels))
        ),
        WxComponents.spacer(20),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_float_with_enable,
            name='trigger_value',
            label='Trigger',
            style_theme=WxComponents.styles.toggle__on__off,
            value=5.0,
            size=(50, -1),
        )
    )
)
vispy_panel = WxComponents.vispypanel(
    parent='main_frame',
    name='vispy_plot',
    shape=(1, 2),
    size=(300, 300),
)

control_panel_all_widgets = WxComponents.panel(
    parent='main_frame',
    name='control_examples',
    sizer_direction='horizontal',
    content=(
        WxComponents.spacer(15),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='gbutton',
            label=f'GB Button',
            value=True,
            style_theme=WxComponents.styles.c5,
            mouse_click_function=True,
            end_space=5,
            size=(-1, -1),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.Button,
            name='button',
            label=f'Button - doubleclick',
            style_theme=WxComponents.styles.green,
            mouse_doubleclick_function=True,
            end_space=5,
            size=(-1, -1),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_float_with_enable,
            name='input_float_enable',
            label='Float Enable',
            style_theme=WxComponents.styles.toggle__on__off,
            value=5.5,
            size=(50, -1),
            end_space=5,
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_int_with_enable,
            name='input_int_enable',
            label='Int Enable',
            style_theme=WxComponents.styles.toggle__on__off,
            value=4,
            size=(50, -1),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_float,
            name='input_float',
            label='Input float',
            style_theme=WxComponents.styles.black,
            value=3.3,
            size=(50, -1),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_int,
            name='input_int',
            label='Input int',
            style_theme=WxComponents.styles.red,
            value=2,
            size=(50, -1),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_text,
            name='input_text',
            label='Input text',
            style_theme=WxComponents.styles.green,
            value='some text',
            size=(120, -1),
        ),
        WxComponents.widget(
            name="static_text",
            label="Static text",
            widget_type=WxComponents.widgets.static_text,
            style_theme=WxComponents.styles.blue,
            mouse_enter_function=True,
            mouse_leave_function=True,
        ),
        WxComponents.widget(
            name="choice",
            widget_type=WxComponents.widgets.choice,
            label='Choices',
            style_theme=WxComponents.styles.black,
            choices=['A', 'B', 'C', 'D', 'E', 'default'],
            value='D',
        ),
        WxComponents.spacer(5),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='rightclick_button',
            label=f'RightClick',
            value=True,
            style_theme=WxComponents.styles.c5,
            mouse_click_function=True,
            mouse_rightclick_function=True,
            end_space=1,
            size=(-1, -1),
        ),
    )
)


if __name__ == '__main__':
    main()
