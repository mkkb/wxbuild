import wx
from wxbuild.components.mainframe import MainFrame, AppConfiguration, WxComponents
from app_master__gradient_buttons import GradientButtonMaster


def main():
    app = wx.App()

    app_config = AppConfiguration(title='WoodPecker', extra_folder='WellGuard', asset_folder="/assets")
    app_config.icon_path = r"C:\KRISTIAN\Python Scripts\GitLab_repos\WellGuard_AS\wg_gui_fpga_wcan\assets\logo_32x32.png"
    app_config.monitor_resources = False

    frm = MainFrame(app_config=app_config)
    frm.master = GradientButtonMaster(main_frame=frm)

    layout_tuple = (
        btn_panel,
        motor_control_panel,
    )
    frm.set_widget_state_map(widget_state_map)
    frm.populate_frame(layout_tuple)

    frm.Show()

    app.MainLoop()


#
btn_sizes = (
    (-1, -1), (-1, 50), (50, -1), (50, 35), (50, 30), (50, 25), (50, 20), (50, 15), (50, 10), (50, 7),
    (-1, 40), (40, 40), (35, 40), (30, 40), (25, 40), (20, 40), (15, 40), (10, 40), (8, 40), (5, 40),
)
#
bg_color = '#F3F0F3' #  green  #d6ffe2      grey  #e8e9e9
state_style = 'white'
page_select_style = 'light_blue'
#
widget_state_map = {
    'connections': {
        0: WxComponents.styles.black, # black
        1: WxComponents.styles.green,
        2: WxComponents.styles.red,
        3: WxComponents.styles.orange,
        4: WxComponents.styles.blue,
        5: WxComponents.styles.light_green,
    },
}

btn_panel = WxComponents.panel(
    parent='main_frame',
    name='grd_btns',
    sizer_direction='horizontal',
    background_color=bg_color,
    content=(
        WxComponents.spacer(),
        *[
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                label=f'Btn{i}',
                name=f'Btn{i}',
                font_size=2,
                end_space=10,
                size=btn_sizes[i],
                mouse_click_function=True,
            ) for i in range(20)
        ],
        WxComponents.spacer(),
    )
)
motor_control_panel = WxComponents.panel(
parent='main_frame',
    name='motorctrls',
    sizer_direction='horizontal',
    background_color=bg_color,
    sizer_border=5,
    sizer_flags=wx.EXPAND | wx.TOP,
    content=(
        *[
            *[
                WxComponents.widget(
                    name=f'ctrl_{i}_0',
                    widget_type=wx_type,
                    font_size=2,
                    end_space=10,
                    mouse_click_function=True,
                )
            for i, wx_type in enumerate([
                WxComponents.widgets.MotorControlDriveState,
                WxComponents.widgets.MotorCtrlRpmCurrent,
                WxComponents.widgets.MotorControlAlarmState,
            ])],
            WxComponents.spacer(20),
            *[
                WxComponents.widget(
                    name=f'ctrl_{i}_1',
                    widget_type=wx_type,
                    font_size=2,
                    end_space=10,
                    mouse_click_function=True,
                )
            for i, wx_type in enumerate([
                WxComponents.widgets.MotorControlDriveState,
                WxComponents.widgets.MotorCtrlRpmCurrent,
                WxComponents.widgets.MotorControlAlarmState,
            ])],
            WxComponents.spacer(20),
            *[
                WxComponents.widget(
                    name=f'ctrl_{i}_2',
                    widget_type=wx_type,
                    font_size=2,
                    end_space=10,
                    mouse_click_function=True,
                )
            for i, wx_type in enumerate([
                WxComponents.widgets.MotorControlDriveState,
                WxComponents.widgets.MotorCtrlRpmCurrent,
                WxComponents.widgets.MotorControlAlarmState,
            ])]
        ],
    ),
)


if __name__ == '__main__':
    main()
