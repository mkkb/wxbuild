import wx

import wxbuild.master_abstract as master
import wxbuild.components.styles_colors as wxcolors

import demos.demo1.threaded_function_test as thread_func

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
        self.plot_update_counter = 0

        self.test_thread_indx = wx.NewIdRef()

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

        # self.vispy_tooltip_window = wx.Panel(self.main_frame, id=wx.ID_ANY, pos=(20, 20), size=(200, 200),
        #                                 style=wx.TAB_TRAVERSAL, name="vispy_tooltip")
        # self.vispy_tooltip_window.SetBackgroundColour(wx.Colour("#ccDDcc"))

        self.main_frame.rich_text.SetMinSize(wx.Size(10, 10))
        self.main_frame.rich_text.set_configuration(max_characters=30_000, max_line_writes_per_frame=50)

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
                self.start_the_thread_monitor()
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
    def start_the_thread_monitor(self):
        print('GUI TRYING TO START A THREAD')
        self.main_frame.init_thread_worker(
            worker_id=self.test_thread_indx,
            run_func=thread_func.threaded_monitor_function,
            run_once=True,
            callback_func=self.handle_thread_response,
            kwargs={'func_info_str': '... this is test thread ...'}
        )

    def handle_thread_response(self, *args, **kwargs):
        event = args[0]
        print('thread_response::: ', args, kwargs)
        print(' workers:', self.main_frame.thread_worker_table)
        print(" event.data::", event.data)
    #
    def init_vispy_plots(self):
        self.plt_n = 2**17
        t = np.arange(self.plt_n) / 250e3
        self.plt_data = 0.02 * np.sin(2*np.pi*25e3*t) + 0.3 * np.sin(2*np.pi*4e3*t)
        self.plt_data_2 = 1.7 * np.sin(2 * np.pi * 400 * t) + 1

        # self.plt_pointer = 0
        #
        self.main_frame.vispy_plot.add_vertical_line(view_index=0, pos=1.0)
        self.main_frame.vispy_plot.add_vertical_line(view_index=0, pos=2.0)
        self.main_frame.vispy_plot.add_vertical_line(view_index=0, pos=3.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=0, pos=1.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=0, pos=2.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=0, pos=3.0)
        self.main_frame.vispy_plot.add_vertical_line(view_index=1, pos=1.0)
        self.main_frame.vispy_plot.add_vertical_line(view_index=1, pos=2.0)
        self.main_frame.vispy_plot.add_vertical_line(view_index=1, pos=3.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=1, pos=1.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=1, pos=2.0)
        self.main_frame.vispy_plot.add_horizontal_line(view_index=1, pos=3.0)

        # self.main_frame.vispy_plot.add_line_set(view_index=0, n_lines=4, n_per_line=self.plt_n)
        # self.main_frame.vispy_plot.add_line_set(view_index=1, n_lines=4, n_per_line=self.plt_n)
        #
        # y0 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n]
        # y1 = np.roll(self.plt_data, - self.plt_pointer)[:self.plt_n] + 2
        # y2 = self.plt_data_2[:self.plt_n]
        # # self.main_frame.vispy_plot.update_line(y_data=y0, line_index=0)
        # # self.main_frame.vispy_plot.update_line(y_data=y1, line_index=1)
        # self.main_frame.vispy_plot.update_line_split_view(
        #     line_index=0, view_index=0, y_data=y0, x_data=t[:self.plt_n], label="Channel 0", color='auto', split_view=(0,0))
        # self.main_frame.vispy_plot.update_line_split_view(
        #     line_index=1, view_index=0, y_data=y1, x_data=t[:self.plt_n], label="Channel 1", color='auto', split_view=(1,0))
        # self.main_frame.vispy_plot.update_line_split_view(
        #     line_index=2, view_index=0, y_data=y2, x_data=t[:self.plt_n], label="Channel 2", color='auto', split_view=(0,1))
        # self.main_frame.vispy_plot.update_line(
        #     line_index=0, view_index=1, y_data=y0, x_data=t[:self.plt_n], label="Channel 00", color='auto')
        # self.main_frame.vispy_plot.update_line(
        #     line_index=1, view_index=1, y_data=y1, x_data=t[:self.plt_n], label="Channel 11", color='auto')

        d = np.zeros(shape=(self.plt_n, 2), dtype=np.float32)
        d[:, 1] = self.plt_data[:]
        d[:, 0] = t
        self.main_frame.vispy_plot.add_line_set(view_index=0, n_lines=7, n_per_line=self.plt_n)
        self.main_frame.vispy_plot.add_line_set(view_index=1, n_lines=7, n_per_line=self.plt_n)
        mapper = [
            {'data': d, 'i_l':0, 'i_v':0, 'i_c':0, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(0,0), 'label': 'current_data'},
            {'data': d, 'i_l':1, 'i_v':0, 'i_c':4, 'y_unit':"bar", 'x_unit':'ms', 'split_view':(1,0), 'label': 'pressure_data'},
            {'data': d, 'i_l':2, 'i_v':0, 'i_c':1, 'y_unit':"RPM", 'x_unit':'ms', 'split_view':(0,1), 'label': 'pump_rpm'},
            {'data': d, 'i_l':3, 'i_v':0, 'i_c':2, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(1,1), 'label': 'pump_current'},
            {'data': d, 'i_l':0, 'i_v':1, 'i_c':1, 'y_unit':"RPM", 'x_unit':'ms', 'split_view':(0,1), 'label': 'rotor_rpm'},
            {'data': d, 'i_l':1, 'i_v':1, 'i_c':2, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(1,1), 'label': 'rotor_current'},
            {'data': d, 'i_l':2, 'i_v':1, 'i_c':3, 'y_unit':"rad", 'x_unit':'ms', 'split_view':(2,1), 'label': 'rotor_position'},
        ]
        for i, map_dict in enumerate(mapper):
            c = wxcolors.ColorsCyclic.get_color_by_index(map_dict['i_c'])
            self.main_frame.vispy_plot.update_line_split_view(
                view_index = map_dict['i_v'],
                line_index = map_dict['i_l'],
                y_data = map_dict['data'][:, 1],
                x_data = map_dict['data'][:, 0],
                label = map_dict['label'],
                color = c,
                split_view = map_dict['split_view'],
            )
            line = self.main_frame.vispy_plot.data_sets[map_dict['i_v']][map_dict['i_l']]
            line.x_unit = map_dict['x_unit']
            line.y_unit = map_dict['y_unit']

        self.main_frame.vispy_plot.show_legend_panel = False
        self.main_frame.vispy_plot.show_tooltip_panel = True
        self.main_frame.vispy_plot.post_init()

    def update_vispy_plots(self):
        # self.plot_update_counter += 1
        # if self.plot_update_counter % 1 == 0:
        #     time_now = time.time()
        #     ms = int(time_now*1000)%1000
        #     tss = time.strftime("%M:%S", time.localtime())
        #     print(f"# update vispy buffers ::  {tss}.{ms:<03d}")

        # print(" self.plt_set:: ", self.plt_set)

        # y0 = np.roll(self.plt_data, - self.plt_pointer//2)[:self.plt_n - int(self.plt_n*0.5) * self.plt_set]
        # y1 = np.roll(self.plt_data, - self.plt_pointer//6)[:self.plt_n - int(self.plt_n*0.3) * self.plt_set] + 2
        # y2 = np.roll(self.plt_data_2, - self.plt_pointer//3)[:self.plt_n - int(self.plt_n*0.9) * self.plt_set]
        #
        # # if self.plt_set == 0:
        # for i in range(1):
        #     self.main_frame.vispy_plot.update_line_split_view(y_data=y0, line_index=0, view_index=0)
        #     self.main_frame.vispy_plot.update_line_split_view(y_data=y1, line_index=1, view_index=0)
        #     self.main_frame.vispy_plot.update_line_split_view(y_data=y2, line_index=2, view_index=0)
        # self.plt_pointer = self.plt_pointer + 50

        t = np.arange(self.plt_n) / 250e3
        # self.plt_data = 0.02 * np.sin(2*np.pi*25e3*t) + 0.3 * np.sin(2*np.pi*4e3*t)
        # self.plt_pointer = 0
        # self.plt_n = t.size
        d = np.zeros(shape=(self.plt_n, 2), dtype=np.float32)
        d[:, 1] = self.plt_data[:]
        d[:, 0] = t[:]
        mapper = [
            {'data': d, 'i_l':0, 'i_v':0, 'i_c':0, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(0,0), 'label': 'current_data'},
            {'data': d, 'i_l':1, 'i_v':0, 'i_c':4, 'y_unit':"bar", 'x_unit':'ms', 'split_view':(1,0), 'label': 'pressure_data'},
            {'data': d, 'i_l':2, 'i_v':0, 'i_c':1, 'y_unit':"RPM", 'x_unit':'ms', 'split_view':(0,1), 'label': 'pump_rpm'},
            {'data': d, 'i_l':3, 'i_v':0, 'i_c':2, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(1,1), 'label': 'pump_current'},
            {'data': d, 'i_l':0, 'i_v':1, 'i_c':1, 'y_unit':"RPM", 'x_unit':'ms', 'split_view':(0,1), 'label': 'rotor_rpm'},
            {'data': d, 'i_l':1, 'i_v':1, 'i_c':2, 'y_unit':"mA", 'x_unit':'ms', 'split_view':(1,1), 'label': 'rotor_current'},
            {'data': d, 'i_l':2, 'i_v':1, 'i_c':3, 'y_unit':"rad", 'x_unit':'ms', 'split_view':(2,1), 'label': 'rotor_position'},
        ]

        for i, map_dict in enumerate(mapper):
            data = map_dict['data']
            if data is not None:
                y = data[1, -512:]
                self.main_frame.vispy_plot.update_line_split_view(
                    y_data=y, line_index=map_dict['i_l'], view_index=map_dict['i_v'])

        self.main_frame.vispy_plot.refresh_lines()

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
            'title': 'Connection Settings',
            'state_key_prefix': 'connection_configuration',
            'callback_func': self.settings_edit_set_default_values,
            'content': {
                'Ethernet': 'label',
                'IP': str,
                'Port': int,
                'Uart': 'label',
                'Uart_Baudrate': (125, 250, 375),
                'Uart_Description': str,
                'CAN': 'label',
                'CAN_Baudrate': (125, 250),
            },
        }
        print(" ::: ")
        print(self.main_frame.state)

        self.main_frame.create_config_popup(setup_dict)

    def settings_edit_set_default_values(self, event):
        print(" SETTING DEFAULT VALUES ")
        prefix_names = 'connection_configuration'
        default_values = {
            'IP': '192.168.40.10',
            'Port': '10',
            'Uart_Baudrate': '375',
            'Uart_Description': 'x35812d',
            'CAN_Baudrate': '250',
        }
        for key, el in default_values.items():
            widget = self.main_frame.get_widget_by_names(panel_name=prefix_names, widget_name=key.lower())
            current_val = widget.wx_widget.get_value()

            print(" widget::", widget, 'current_val:', current_val, ' default_val:', el, " ||| ", widget.wx_widget.get_value())
            widget.wx_widget.set_value(el)
            self.main_frame.set_state_value(state_key=widget.wx_widget.state_key, value=widget.wx_widget.get_value())


    #
    def vispy_mouseclick(self, event):
        # self.main_frame.vispy_plot.legend_panel.SetTransparent(50)
        # color = self.main_frame.vispy_plot.legend_panel.GetBackgroundColour()
        # pos = self.main_frame.vispy_plot.legend_panel.GetPosition()
        # print(" color:: ", color)
        # print(" pos::", pos)
        # pos = ((pos[0] + 25)%1000, pos[1])
        #
        # # color.Set(color.Red(), color.Green(), (color.Blue() + 10)%255, (color.Alpha() + 30)%255)
        # color.Set(20, 255, 25, (color.Alpha() + 30)%255)
        # self.main_frame.vispy_plot.legend_panel.SetBackgroundColour(color)
        # self.main_frame.vispy_plot.legend_panel.SetOwnBackgroundColour(color)
        # # self.main_frame.vispy_plot.legend_panel.SetWindowStyle(wx.TRANSPARENT_WINDOW) # BG_STYLE_TRANSPARENT BG_STYLE_COLOUR
        # self.main_frame.vispy_plot.legend_panel.SetTransparent(50)
        # self.main_frame.vispy_plot.legend_panel.SetPosition(pos)
        # self.main_frame.vispy_plot.legend_panel.Refresh()
        pass

    def vispy_mousemove(self, event):
        # print(" event", dir(event))
        # print(" ev_pos", event.pos, self.main_frame.vispy_plot.mouse_x, self.main_frame.vispy_plot.mouse_y)
        # print("   -", self.main_frame.vispy_plot.GetPosition())
        # print("   -", self.main_frame.vispy_plot.GetSize())
        #
        # self.main_frame.vispy_plot.legend_panel.SetPosition(
        #     (event.pos[0] + 10, event.pos[1] - 10)
        # )

        # self.vispy_tooltip_window.Hide()
        # self.vispy_tooltip_window.Show()
        pass
