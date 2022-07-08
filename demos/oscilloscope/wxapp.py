from wxbuild.components.mainframe import MainFrame, AppConfiguration, WxComponents

from wx import App


def main():
    app = App()

    app_config = AppConfiguration
    app_config.title = 'Pseudo Kistler Oscilloscope'
    app_config.monitor_resources = True

    frm = MainFrame(app_config=app_config)

    layout_tuple = (
        control_panel,
        vispy_panel,
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
                label=f'CH{i+1}',
                value=True,
                theme_scheme_name=WxComponents.schemes.green,
                mouse_click_function=True,
                end_space=4,
                size=(60, 40),
            ) for i in range(4)
        ),
        WxComponents.spacer(50),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                label=f'{other_ctrl_button_labels[i]}',
                value=not i%5,
                theme_scheme_name=WxComponents.schemes.cyan,
                mouse_click_function= True,
                end_space=4,
                size=(60, 40),
            ) for i in range(4)
        ),
        WxComponents.spacer(20),
        WxComponents.widget(
            widget_type=WxComponents.widgets.input_float_with_enable,
            label='Trigger',
            theme_scheme_name=WxComponents.schemes.toggle__on__off,
            mouse_click_function= True,
            value=5.0,
            size=(60, 40),
        )
    )
)
vispy_panel = WxComponents.vispypanel(
    parent='main_frame',
    name='vispy_plot',
    shape=(1, 2),
)


if __name__ == '__main__':
    main()
