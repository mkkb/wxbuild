import wx

import wxbuild.master_abstract as master
import wxbuild.components.styles_colors as wxcolors

import numpy as np
import time


class Master(master.Master):
    def __init__(self, main_frame):
        self.main_frame = main_frame
        print(" master initiation..........................................")

        # Connection state (Eth, Uart, Can)
        self.connectivity_selected = ''
        self.connectivity_state = 0

        self.font_medium_big = wx.Font(
            pointSize=12, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
            weight=wx.FONTWEIGHT_MEDIUM, underline=False,
            faceName="", encoding=wx.FONTENCODING_DEFAULT
        )
        self.font_medium_medium = wx.Font(
            pointSize=11, family=wx.FONTFAMILY_DEFAULT, style=wx.FONTSTYLE_NORMAL,
            weight=wx.FONTWEIGHT_SEMIBOLD, underline=False,
            faceName="", encoding=wx.FONTENCODING_DEFAULT
        )
        self.pages = ['main', 'traffic', 'statistics', 'log', 'setup', 'processing', 'dataset',]
        self.page_select_style = 'light_blue'
        self.page_select_style_not_selected = 'lighter_blue'

        self.rich_text_line_counter = 0
        self.plt_set = 0

    def post_init(self):
        print("\n-- POST Initiation of Master --\n")
        # Enforce fps of selected interval
        self.main_frame.add_timer(interval=100)

        #
        self.update_rich_text_bool = False
        self.main_frame.add_idle_function(func=self.update_rich_text, timeout=100)

        self.init_vispy_plots()
        self.main_frame.add_idle_function(func=self.update_vispy_plots, args=None, timeout=150)

    def post_vispy_init(self):
        monitor_sizes = self.main_frame.get_monitor_sizes()
        smallest_screen = monitor_sizes[0][1]
        self.main_frame.maximize_in_monitor(smallest_screen)
        self.main_frame.vispy_plot.Hide()
        #
        self.main_frame.vispy_plot.mouseclick_callback = self.vispy_mouseclick
        self.main_frame.vispy_plot.mousemove_callback = self.vispy_mousemove

        self.main_frame.rich_text.SetMinSize(wx.Size(10, 10))
        self.main_frame.Layout()

    def handle_user_event(self, event_type, name, panel):
        print(f" HANDLING USER EVENT:::  type: {event_type} | name: {name} | panel: {panel}")
        if panel == 'connections':
            if event_type == 'right_click':
                self.settings_edit_IO(widget_name=name)
            else:
                self.connectivity_state = (self.connectivity_state + 1) % 6
                self.main_frame.set_state_of_widget(state=self.connectivity_state, widget_name=name, panel_name=panel)
        elif panel == 'control':
            if name == 'hydraulic_state_a':
                # print(" --> ", dir(self.main_frame.vispy_plot))
                self.main_frame.vispy_plot.toggle_axis()
            elif name == 'hydraulic_state_b':
                self.plt_set = (self.plt_set + 1) % 2
                # self.update_vispy_buffers()
            elif name == 'hydraulic_state_c':
                # self.update_vispy_buffers()
                self.zoom_home_vispy()
            #
            elif name == 'tx_selected_1':
                self.reset_rich_text()
            elif name == 'tx_selected_2':
                self.clear_rich_text()
            elif name == 'tx_selected_3':
                self.add_mask_rich_text()
            elif name == 'tx_selected_4':
                pass
        elif panel == 'page_select':
            self.page_view_selected = name
            print(" selected page::", self.page_view_selected)
            for page in self.pages:
                if self.page_view_selected == page:
                    #self.main_frame.set_label_of_widget(text=name, widget_name=name, panel_name=panel)
                    self.main_frame.set_font_of_widget(font=self.font_medium_big, widget_name=page, panel_name=panel)
                    self.main_frame.set_color_of_widget(color=self.page_select_style, widget_name=page, panel_name=panel)
                else:
                    self.main_frame.set_font_of_widget(font=self.font_medium_medium, widget_name=page, panel_name=panel)
                    self.main_frame.set_color_of_widget(color=self.page_select_style_not_selected, widget_name=page, panel_name=panel)

            self.update_rich_text_bool = False
            if name == 'main':
                self.main_frame.vispy_plot.Show()
                self.main_frame.rich_text.Hide()
            elif name == 'log':
                if self.main_frame.rich_text.IsShown():
                    self.update_rich_text_bool = True
            else:
                self.main_frame.vispy_plot.Hide()
                self.main_frame.rich_text.Show()

            self.main_frame.Layout()

    #
    def init_vispy_plots(self):
        t = np.arange(2**17) / 250e3
        self.plt_data = 0.02 * np.sin(2*np.pi*25e3*t) + 0.3 * np.sin(2*np.pi*4e3*t)
        self.plt_pointer = 0
        self.plt_n = 1024
        #
        self.main_frame.vispy_plot.add_vertical_line(view_index=0, pos=0.5)
        self.main_frame.vispy_plot.add_vertical_line(view_index=1, pos=0.5)
        self.main_frame.vispy_plot.add_line_set(view_index=0, n_lines=2, n_per_line=self.plt_n)
        self.main_frame.vispy_plot.add_line_set(view_index=1, n_lines=2, n_per_line=self.plt_n)

        y0 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n]
        y1 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n] + 2
        # self.main_frame.vispy_plot.update_line(y_data=y0, line_index=0)
        # self.main_frame.vispy_plot.update_line(y_data=y1, line_index=1)
        self.main_frame.vispy_plot.update_line(line_index=0, view_index=0, y_data=y0, x_data=t[:self.plt_n], color=wxcolors.ColorsCyclic.get_color())
        self.main_frame.vispy_plot.update_line(line_index=1, view_index=0, y_data=y1, x_data=t[:self.plt_n], color=wxcolors.ColorsCyclic.get_color())
        self.main_frame.vispy_plot.update_line(line_index=0, view_index=1, y_data=y0, x_data=t[:self.plt_n], color=wxcolors.ColorsCyclic.get_color())
        self.main_frame.vispy_plot.update_line(line_index=1, view_index=1, y_data=y1, x_data=t[:self.plt_n], color=wxcolors.ColorsCyclic.get_color())

    def update_vispy_plots(self):
        # print("# update vispy buffers", time.strftime("%M:%S", time.localtime()))
        y0 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n - self.plt_n//2 * self.plt_set]
        y1 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n - self.plt_n//2 * self.plt_set] + 2
        self.main_frame.vispy_plot.update_line(y_data=y0, line_index=0, view_index=self.plt_set)
        self.main_frame.vispy_plot.update_line(y_data=y1, line_index=1, view_index=self.plt_set)
        self.plt_pointer = self.plt_pointer + 50

    def update_vispy_buffers(self):
        # y0 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n - self.plt_n//2 * self.plt_set]
        # y1 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n - self.plt_n//2 * self.plt_set]
        # self.plt_pointer = self.plt_pointer + 50

        print(" toggling plot set:: ", self.plt_set)
        # self.main_frame.vispy_plot.update_line(y_data=y0, line_index=0)
        # self.main_frame.vispy_plot.update_line(y_data=y1, line_index=1)

    def zoom_home_vispy(self):
        self.main_frame.vispy_plot.zoom_axis_home()

    #
    def update_rich_text(self):
        if self.main_frame.rich_text.IsShown():
            if self.update_rich_text_bool:
                # print(" updating richtext....")
                new_txt = ""
                n = 80
                for i in range(n):
                    data = f":".join([f"0x{x:02X}" for x in np.random.randint(0, 255, size=8, dtype=np.uint8)])
                    new_txt += f"\n Source: {0}   |   Destination: {10+i}   " \
                               f"|   {data}  |  {int(time.perf_counter_ns()//1e3)%600_000_000}  " \
                               f"|   count = {i + self.rich_text_line_counter}"
                self.rich_text_line_counter += n
                print(" text_size == ", len(new_txt))
                self.main_frame.rich_text.add_to_text(new_txt)
            else:
                self.main_frame.rich_text.update_widget()

    def reset_rich_text(self):
        self.main_frame.rich_text.clear_displayed_text()

    def clear_rich_text(self):
        self.main_frame.rich_text.clear_text()

    def add_mask_rich_text(self):
        self.main_frame.rich_text.add_mask()

    #
    def settings_edit_IO(self, widget_name):
        print("\nCreating POPUP window:: ", widget_name)
        setup_dict = {
            'Ethernet': 'label',
            'IP': str,
            'Port': int,
            'Uart': 'label',
            'Uart_Baudrate': [125, 250, 375],
            'Uart_Description': str,
            'CAN': 'label',
            'CAN_Baudrate': [125, 250],
        }
        print(" ::: ")
        print(self.main_frame.state)

        self.main_frame.create_config_popup(setup_dict, state_key_prefix='connection_config')

    #
    def vispy_mouseclick(self, event):
        # self.main_frame.vispy_plot.legend_panel.SetTransparent(50)
        color = self.main_frame.vispy_plot.legend_panel.GetBackgroundColour()
        pos = self.main_frame.vispy_plot.legend_panel.GetPosition()
        print(" color:: ", color)
        print(" pos::", pos)
        pos = ((pos[0] + 25)%1000, pos[1])

        # color.Set(color.Red(), color.Green(), (color.Blue() + 10)%255, (color.Alpha() + 30)%255)
        color.Set(20, 255, 25, (color.Alpha() + 30)%255)
        self.main_frame.vispy_plot.legend_panel.SetBackgroundColour(color)
        self.main_frame.vispy_plot.legend_panel.SetOwnBackgroundColour(color)
        # self.main_frame.vispy_plot.legend_panel.SetWindowStyle(wx.TRANSPARENT_WINDOW) # BG_STYLE_TRANSPARENT BG_STYLE_COLOUR
        self.main_frame.vispy_plot.legend_panel.SetTransparent(50)
        self.main_frame.vispy_plot.legend_panel.SetPosition(pos)
        self.main_frame.vispy_plot.legend_panel.Refresh()

    def vispy_mousemove(self, event):
        pass
