import wx
from wxbuild.components.mainframe import MainFrame, AppConfiguration, WxComponents
import demos.demo1.master as master


def main():
    app = wx.App()

    app_config = AppConfiguration(title='WoodPecker', extra_folder='WellGuard', asset_folder="/assets")
    app_config.icon_path = r"C:\KRISTIAN\Python Scripts\GitLab_repos\WellGuard_AS\wg_gui_fpga_wcan\assets\logo_32x32.png"
    app_config.monitor_resources = True

    frm = MainFrame(app_config=app_config)
    frm.master = master.Master(frm)

    layout_tuple = (
        connection_panel,
        #
        fill_panel,
        control_panel,
        fill_panel,
        status_panel,
        fill_panel,
        #
        page_select_panel,
        vispy_panel,
        richtext_panel,
        control_panel_all_widgets,
    )
    frm.set_widget_state_map(widget_state_map)
    frm.populate_frame(layout_tuple)

    frm.Show()
    app.MainLoop()


connectivity_buttons = ('Eth', 'Uart', 'CAN')
nse_node_buttons = ('Pump', 'Rotation', 'DCDC')
mpb_node_buttons = ('SensorBoard', 'Processing')
init_buttons = ('Ping Nodes', 'Verify Nodes', 'Reset')
pages = ('Main', 'Traffic', 'Statistics', 'Log', 'Setup', 'Processing', 'Dataset')
#
large_btn_height = 30
medium_btn_height = 27
small_btn_height = 24
#
status_widths = 100
page_select_widths = 160
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

fill_panel = WxComponents.panel(
    parent='main_frame',
    name='fills',
    sizer_direction='horizontal',
    background_color=bg_color,
    content=(
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'',
            font_size=2,
            end_space=0,
            size=(1, 1),
        ),
    )
)
connection_panel = WxComponents.panel(
    parent='main_frame',
    name='connections',
    sizer_direction='horizontal',
    sizer_border=3,
    sizer_flags=wx.EXPAND | wx.BOTTOM,
    content=(
        WxComponents.spacer(15),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{label}'.lower(),
                label=f'{label}',
                value=0,
                state_map='connections',
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                mouse_rightclick_function=True,
                end_space=4,
                size=(40, medium_btn_height),
            ) for label in connectivity_buttons
        ),
        WxComponents.spacer(100),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=4,
                size=(80, medium_btn_height),
            ) for label in nse_node_buttons
        ),
        WxComponents.spacer(15),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=4,
                size=(80, medium_btn_height),
            ) for label in mpb_node_buttons
        ),
        WxComponents.spacer(100),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.cyan,
                mouse_click_function=True,
                end_space=4,
                size=(80, medium_btn_height),
            ) for label in init_buttons
        ),
    )
)
control_panel = WxComponents.panel(
    parent='main_frame',
    name='control',
    sizer_direction='horizontal',
    sizer_border=0,
    sizer_flags=wx.EXPAND | wx.BOTTOM,
    background_color=bg_color,
    content=(
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'Hydraulic State:',
            end_space=2,
            size=(-1, small_btn_height),
        ),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'hydraulic_state_{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=2,
                size=(-1, small_btn_height),
            ) for label in ['A', 'B', 'C']
        ),
        WxComponents.spacer(20),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'SOVs:',
            end_space=2,
            size=(-1, small_btn_height),
        ),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'sovs_{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=2,
                size=(-1, small_btn_height),
            ) for label in ['1', '2']
        ),
        WxComponents.spacer(60),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'Number of rotations:',
            end_space=2,
            size=(-1, small_btn_height),
        ),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'n_rotations_{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=2,
                size=(-1, small_btn_height),
            ) for label in ['3', '6', '9', '12']
        ),
        WxComponents.spacer(20),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'Position:',
            end_space=2,
            size=(-1, small_btn_height),
        ),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'rotation_position_{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=2,
                size=(-1, small_btn_height),
            ) for label in [str(i+1) for i in range(12)]
        ),
        WxComponents.spacer(60),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'Tx selected:',
            end_space=2,
            size=(-1, small_btn_height),
        ),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'tx_selected_{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=WxComponents.styles.black,
                mouse_click_function=True,
                end_space=2,
                size=(-1, small_btn_height),
            ) for label in [str(i+1) for i in range(4)]
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name=f'tx_selected_off'.lower(),
            label='Off',
            value=0,
            style_theme=WxComponents.styles.black,
            mouse_click_function=True,
            end_space=5,
            size=(-1, small_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label=f'  :::  ',
            end_space=5,
            size=(-1, small_btn_height),
        ),
        WxComponents.spacer(20),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name=f'daq_control_daq'.lower(),
            label='DAQ',
            value=0,
            style_theme=WxComponents.styles.black,
            mouse_click_function=True,
            end_space=2,
            size=(-1, small_btn_height),
        ),
    )
)
status_panel = WxComponents.panel(
    parent='main_frame',
    name='status',
    sizer_direction='horizontal',
    # sizer_border=0,
    # sizer_flags=wx.EXPAND | wx.BOTTOM | wx.TOP | wx.RIGHT,
    background_color=bg_color,
    content=(
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label='I dcdc [mA]:',
            end_space=2,
            size=(-1, medium_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='i_dcdc',
            label='',
            value=0,
            style_theme=state_style,
            mouse_click_function=True,
            end_space=4,
            size=(status_widths, medium_btn_height),
        ),
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label='MPB temp [°C]:',
            end_space=2,
            size=(-1, medium_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='mpb_temp',
            label='',
            value=0,
            style_theme=state_style,
            mouse_click_function=True,
            end_space=4,
            size=(status_widths, medium_btn_height),
        ),
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label='Pressure [bar]:',
            end_space=2,
            size=(-1, medium_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='pressure',
            label='',
            value=0,
            style_theme=state_style,
            mouse_click_function=True,
            end_space=4,
            size=(status_widths, medium_btn_height),
        ),
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label='Est. depth [m]:',
            end_space=2,
            size=(-1, medium_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='estimated_depth',
            label='',
            value=0,
            style_theme=state_style,
            mouse_click_function=True,
            end_space=4,
            size=(status_widths, medium_btn_height),
        ),
        WxComponents.spacer(10),
        WxComponents.widget(
            widget_type=WxComponents.widgets.static_text,
            label='Log:',
            end_space=2,
            size=(-1, medium_btn_height),
        ),
        WxComponents.widget(
            widget_type=WxComponents.widgets.GradientButton,
            name='log',
            label='',
            value=0,
            style_theme=state_style,
            mouse_click_function=True,
            end_space=4,
            size=(1300, medium_btn_height),
        ),
        WxComponents.spacer(5),
    )
)
page_select_panel = WxComponents.panel(
    parent='main_frame',
    name='page_select',
    sizer_direction='horizontal',
    sizer_border=3,
    sizer_flags=wx.EXPAND | wx.TOP | wx.BOTTOM,
    content=(
        WxComponents.spacer(15),
        *tuple(
            WxComponents.widget(
                widget_type=WxComponents.widgets.GradientButton,
                name=f'{label}'.lower(),
                label=f'{label}',
                value=0,
                style_theme=page_select_style,
                mouse_click_function=True,
                end_space=20,
                size=(page_select_widths, medium_btn_height),
            ) for label in pages
        ),
    )
)
vispy_panel = WxComponents.vispypanel(
    parent='main_frame',
    name='vispy_plot',
    shape=(1, 2),
    size=(50, 50),
)
richtext_panel = WxComponents.richtext(
    parent='main_frame',
    name='rich_text',
    shape=(2, 1),
    size=(10, 10),
    sizer_flags=wx.EXPAND,
    sizer_proportion=1,
)
control_panel_all_widgets = WxComponents.panel(
    parent='main_frame',
    name='control_examples',
    sizer_direction='horizontal',
    sizer_border=0,
    sizer_flags=wx.EXPAND | wx.BOTTOM,
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

# config_setup_connections_popup_window = WxComponents.popupwindow(
#     icon_path='icon_cog_wheel_black.png',
#     title='Connection Settings',
#     parent='main_frame',
#     name='config_setup_connections',
#     sizer_direction='vertical',
#     sizer_border=0,
#     sizer_flags=wx.EXPAND | wx.BOTTOM,
#     content=(
#         WxComponents.widget(
#             name="Ethernet",
#             label="Static text",
#             widget_type=WxComponents.widgets.static_text,
#             style_theme=WxComponents.styles.blue,
#             mouse_enter_function=True,
#             mouse_leave_function=True,
#         ),
#         WxComponents.widget(
#             widget_type=WxComponents.widgets.input_text,
#             name='input_text',
#             label='Input text',
#             style_theme=WxComponents.styles.green,
#             value='',
#             size=(120, -1),
#         ),
#     )
    # setup_dict = {
    #             'Title': 'Connection Settings',
    #             'Ethernet': 'label',
    #             'IP': str,
    #             'Port': int,
    #             'Uart': 'label',
    #             'Uart_Baudrate': [125, 250, 375],
    #             'Uart_Description': str,
    #             'CAN': 'label',
    #             'CAN_Baudrate': [125, 250],
    #         }
# )

if __name__ == '__main__':
    main()
