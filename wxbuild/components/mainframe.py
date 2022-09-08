import datetime
import logging
import sys
import time
import os
import tempfile
import json
from threading import Thread
from dataclasses import dataclass

import numpy as np
import wx
import psutil

import wxbuild.components.widget as wg
import wxbuild.components.panel_with_state as wxp
import wxbuild.components.panel_vispy as wxv
import wxbuild.components.panel_richtext as wxr
import wxbuild.master_abstract as master
from wxbuild.components.styles import Styles


@dataclass
class AppConfiguration:
    """Main frame configuration, set title, folder location, etc..."""
    title: str = 'wxDemo'
    extra_folder: str = ""
    state_folder: str = rf'{tempfile.gettempdir()}{os.path.sep}{title}{os.path.sep}'
    state_path: str = rf'{state_folder}{os.path.sep}state.json'
    status_bar_default_text: str = f'Welcome to {title}'
    monitor_resources: bool = False
    bc_color: str = 'white'
    asset_folder: str = ""

    @classmethod
    def reset_paths(cls):
        if len(cls.extra_folder) > 0:
            cls.state_folder = rf'{tempfile.gettempdir()}' \
                                rf'{os.path.sep}{cls.extra_folder}' \
                                rf'{os.path.sep}{cls.title}' \
                                rf'{os.path.sep}'
        else:
            cls.state_folder = rf'{tempfile.gettempdir()}' \
                                rf'{os.path.sep}{cls.title}' \
                                rf'{os.path.sep}'
        cls.state_path = rf'{cls.state_folder}{os.path.sep}state.json'


@dataclass
class WxComponents:
    panel = wxp.WxPanel
    widget = wg.Widget
    spacer = wxp.Spacer
    vispypanel = wxv.WxPanel
    richtext = wxr.WxPanel
    widgets = wg.Widgets
    styles = Styles


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        if 'app_config' in kwargs:
            self.config = kwargs.pop('app_config')
        else:
            self.config = AppConfiguration
        super().__init__(None, *args, **kwargs)

        self.SetTitle(self.config.title)
        self.screen_w, self.screen_h = wx.DisplaySize()

        self.state = {}
        self.master = master.Master()
        self.load_state()
        self.thread_workers = []
        self.idle_functions = []

        self.double_click_status = MouseDoubleClick()

        if self.config.monitor_resources:
            self.process_info = ProcessInfo()
            self.toolbar = self.CreateToolBar()
            self.monitor_textbox = wx.TextCtrl(self.toolbar, -1, size=(self.screen_w, 40))
            monitor_app_resources__init(self)
            self.add_idle_function(func=monitor_app_resources__loop_frontend, args=self, timeout=0)

        # print( '--', self.get_monitor_size(index=0) )
        # print( '--', self.get_monitor_sizes() )

        self.Bind(wx.EVT_SIZE, self.on_repaint)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.bg_panel = wx.Panel(self)
        self.SetBackgroundColour(self.config.bc_color)
        self.widget_state_map = {}

        self.resized = False
        self.exit = False
        self.init = False

    def post_idle(self):
        self.master.post_init()

    #
    # Event based functions
    def on_close(self, event):
        logging.debug(f'On idle: ', event)
        if hasattr(self, 'on_exit'):
            getattr(self, 'on_exit')()

        wx_id = wx.NewIdRef()
        self.init_thread_worker(
            worker_id=wx_id, callback_func=self.final_exit, run_func=self.kill_all_workers, args=wx_id, run_once=True
        )

    def on_repaint(self, event):
        logging.debug(f'On idle: ', event)
        self.resized = True

    def on_idle(self, event):
        if self.resized:
            logging.debug(f'On idle resized: ', event)
            self.resized = False
            self.Layout()

        for worker in self.thread_workers:
            if not worker.running:
                self.delete_thread_worker(worker.wx_id)

        for i, (func, args, last_time_run, timeout) in enumerate(self.idle_functions):
            if time.perf_counter_ns() - last_time_run > timeout:
                self.idle_functions[i][2] = time.perf_counter_ns()
                if args is not None:
                    func(args)
                else:
                    func()

        if not self.init:
            self.init = True
            self.post_idle()

    def add_idle_function(self, func, args=None, timeout=100):
        '''
        Add function that will be run every time UI is idle and timeout has expired

                Parameters:
                        func (callable): Function to be run
                        args (object | tuple | list): Function argument
                        timeout (int): Time in ms, minumum time between function calls

                Returns:
                        None
        '''
        self.idle_functions.append([func, args, time.perf_counter_ns(), timeout*1e6])

    @staticmethod
    def final_exit(*args):
        logging.debug(f'On final exit: ', args)
        wx.Exit()

    #
    # Saving UI state to temporary file
    def save_state(self):
        if not os.path.exists(self.config.state_path):
            if not os.path.exists(self.config.state_folder):
                os.makedirs(self.config.state_folder)
        with open(self.config.state_path, mode='w') as f_:
            json.dump(self.state, f_)

    def load_state(self):
        if os.path.exists(self.config.state_path):
            with open(self.config.state_path, mode='r') as f_:
                self.state = json.load(f_)

    def reset_state(self):  # TODO
        pass

    def set_state_value(self, state_key, value):
        self.state[state_key] = value
        self.save_state()

    def get_state_value(self, state_key):
        if state_key in self.state:
            return self.state[state_key]

    #
    # Thread workers # Thread workers # Thread workers # Thread workers # Thread workers # Thread workers
    def init_thread_worker(self, run_func, worker_id=-1, callback_func=None, run_once=True, args=None):
        print("\nAppending worker:")
        worker_index = self.get_thread_worker_by_id(worker_id)

        # Create a new thread
        if worker_index is None:
            if callback_func is not None:
                print(" - connecting worker to callback function:", callback_func)
                self.Connect(-1, -1, worker_id, callback_func)
                call_event = True
            else:
                call_event = False
            thread_worker = WorkerThread(
                func=run_func, parent=self, wx_id=worker_id, run_once=run_once, args=args, call_event=call_event
            )

            print(" - thread worker: ", thread_worker, worker_id)
            self.thread_workers.append(thread_worker)
        else:
            print(" - worker already exists...")
            worker = self.thread_workers[worker_index]
            if worker.is_stopped():
                print('Worker is stopped, restart it?\n')

    def delete_thread_worker(self, worker_id):
        worker_index = self.get_thread_worker_by_id(worker_id)
        if worker_index is not None:
            self.thread_workers[worker_index].kill()

    def get_thread_worker_by_id(self, worker_id: int) -> int | None:
        worker_index = None
        for i, worker in enumerate(self.thread_workers):
            if worker_id == worker.get_wx_id():
                worker_index = i
        return worker_index

    def kill_all_workers(self, worker_id_self: int) -> None:
        worker_ids = [worker.get_wx_id() for worker in self.thread_workers if worker.get_wx_id() != worker_id_self]
        # print("Ongoing workers: ")
        # for i, worker in enumerate(self.thread_workers):
        #     print(" -", i, worker.wx_id, worker.running, worker._is_stopped)
        for w_id in worker_ids:
            self.delete_thread_worker(w_id)

    def add_timer(self, interval=50, func=None):
        if func is None:
            def timer_update(*args): pass
            func = timer_update
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, func, self.timer)
        self.timer.Start(interval)

    #
    # For multiple monitors
    @staticmethod
    def get_monitor_sizes() -> dict:
        monitor_sizes = []
        monitor_inches = []
        n_monitors = wx.Display.GetCount()
        for i in range(n_monitors):
            m_width = wx.Display(i).GetGeometry().GetWidth()
            m_height = wx.Display(i).GetGeometry().GetHeight()
            monitor_sizes.append((m_width, m_height))
            monitor_inches.append(np.sqrt(m_height**2 + m_width**2))
        sorted_sizes = [x for _, x in sorted(zip(monitor_inches, monitor_sizes))]
        sorted_indecies = [x for _, x in sorted(zip(monitor_inches, [i for i in range(n_monitors)]))]
        monitor_dict = {i: (sorted_sizes[i], sorted_indecies[i]) for i in range(n_monitors)}
        return monitor_dict

    @staticmethod
    def get_monitor_size(index: int) -> tuple:
        return wx.Display(index).GetGeometry().GetWidth(), wx.Display(index).GetGeometry().GetHeight()

    def move_window_to_monitor(self, target_index: int) -> None:
        self.SetPosition(wx.Display(target_index).GetGeometry().GetTopLeft())

    def maximize_in_monitor(self, screen_index=None) -> None:
        if screen_index is None:
            monitor_dict = self.get_monitor_sizes()
            target_index = monitor_dict[0][1]
        else:
            target_index = screen_index

        self.move_window_to_monitor(target_index)
        self.Maximize(True)

    #
    # Populate entire UI frame from a tuple, nested panels will lead to recursive calls
    def populate_frame(self, layout_tuple: tuple):
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        for i, panel_data in enumerate(layout_tuple):
            panel = None
            if isinstance(panel_data.parent, str):
                parent = self
            else:
                parent = panel_data.parent

            # Normal wx.Panel
            if isinstance(panel_data, wxp.WxPanel):
                panel = wxp.PanelWithState(
                    parent=parent, main_frame=self, panel_name=panel_data.name, content=panel_data.content
                )
                setattr(panel, 'dataclass', panel_data)
                panel.post_init()

            # A vispy panel
            elif isinstance(panel_data, wxv.WxPanel):
                panel = wxv.VispyPanel(main_frame=self, parent=parent, shape=panel_data.shape, size=panel_data.size)
                setattr(panel, 'dataclass', panel_data)
                panel.post_init()

            # Rich text panel
            elif isinstance(panel_data, wxr.WxPanel):
                panel = wxr.RichtextPanel(main_frame=self, parent=parent, shape=panel_data.shape)
                setattr(panel, 'dataclass', panel_data)
                panel.post_init()

            else:
                print("  ->  is not a panel???", parent)
                # wxv.populate_sizer(element)

            if panel is not None:
                setattr(self, panel_data.name, panel)
                if parent == self:
                    top_sizer.Add(panel, panel_data.sizer_proportion, panel_data.sizer_flags, panel_data.sizer_border)

        self.SetSizerAndFit(top_sizer)
        self.Layout()

    #
    # Respond to user actions
    def handle_user_event(self, event):
        # print("\n", "-"*100, "\n USER ACTION:", event.EventObject.wx_widget.widget.name)
        # print(" .. ", event.EventType, vars(event))
        # print("-"*100)
        event_type = ''
        widget_name = event.EventObject.wx_widget.widget.name
        panel_name = event.EventObject.wx_widget.parent.panel_name
        if event.EventType == wx.EVT_BUTTON.typeId:
            if '_with_enable' in event.EventObject.wx_widget.widget.widget_type:
                event_type = 'toggle_input_field'
            else:
                if event.EventObject.wx_widget.widget.mouse_click_function:
                    event_type = 'normal_click'
                if event.EventObject.wx_widget.widget.mouse_doubleclick_function:
                    if self.double_click_status.double_clicked(event.EventObject.wx_widget.widget.name):
                        event_type = 'double_click'
                else:
                    self.double_click_status.reset()
        elif event.EventType == wx.EVT_RIGHT_UP.typeId:
            if event.EventObject.wx_widget.widget.mouse_rightclick_function:
                event_type = 'right_click'
        else:
            if event.EventType == wx.EVT_ENTER_WINDOW.typeId:
                event_type = 'window_enter'
            elif event.EventType == wx.EVT_LEAVE_WINDOW.typeId:
                event_type = 'window_leave'

        self.master.handle_user_event(event_type, widget_name, panel_name)

    def input_state_edit(self, event):
        if event.EventType == wx.EVT_CHAR.typeId:
            new_char = event.GetKeyCode()
            if new_char not in (wx.WXK_BACK, wx.WXK_DELETE, wx.WXK_LEFT, wx.WXK_RIGHT):
                insertion_pos = event.EventObject.wx_widget.input_element.GetInsertionPoint()
                old_value = event.EventObject.wx_widget.input_element.GetValue()
                new_value = old_value[:insertion_pos] + chr(new_char) + old_value[insertion_pos:]

            else:
                if new_char in (wx.WXK_BACK, wx.WXK_DELETE,):
                    insertion_pos = event.EventObject.wx_widget.input_element.GetInsertionPoint()
                    old_value = event.EventObject.wx_widget.input_element.GetValue()
                    if new_char == wx.WXK_BACK:
                        new_value = old_value[:insertion_pos-1] + old_value[insertion_pos:]
                    else:
                        new_value = old_value[:insertion_pos] + old_value[insertion_pos+1:]
                else:
                    event.Skip()
                    return

            if 'input_int' in event.EventObject.wx_widget.widget.widget_type:
                if new_char == wx.WXK_SPACE:
                    return
                else:
                    try:
                        new_value = int(new_value)
                    except ValueError:
                        return
            elif 'input_float' in event.EventObject.wx_widget.widget.widget_type:
                if new_char == wx.WXK_SPACE:
                    return
                else:
                    try:
                        new_value = float(new_value)
                    except ValueError:
                        return

            event.EventObject.wx_widget.set_value_by_event(value=new_value)
            state_key = f'state__{event.EventObject.wx_widget.parent.panel_name}' \
                        f'__{event.EventObject.wx_widget.widget.name}'
        elif event.EventType == wx.EVT_CHOICE.typeId:
            event.EventObject.wx_widget.set_value_by_event(value=None)
            state_key = f'state__{event.EventObject.wx_widget.parent.panel_name}' \
                        f'__{event.EventObject.wx_widget.widget.name}'
        else:
            event.Skip()
            return

        self.set_state_value(state_key=state_key, value=event.EventObject.wx_widget.get_value())
        event.Skip()

    #
    # Widget related actions
    def get_widget_by_names(self, widget_name, panel_name):
        attr_name = f'state__{panel_name}__{widget_name}'
        if hasattr(self, attr_name):
            return getattr(self, attr_name)

    def set_widget_state_map(self, widget_state_map: dict):
        self.widget_state_map = widget_state_map

    def set_state_of_widget(self, state, widget_name, panel_name):
        widget = self.get_widget_by_names(widget_name=widget_name, panel_name=panel_name)
        if widget is not None:
            style = self.widget_state_map[widget.wx_widget.widget.state_map][state]
            widget.wx_widget.set_style_of_widget(widget, style)

    def set_label_of_widget(self, text, widget_name, panel_name):
        widget = self.get_widget_by_names(widget_name=widget_name, panel_name=panel_name)
        if widget is not None:
            widget.wx_widget.set_label(widget, text)

    def set_font_of_widget(self, font, widget_name, panel_name):
        widget = self.get_widget_by_names(widget_name=widget_name, panel_name=panel_name)
        if widget is not None:
            widget.wx_widget.set_font(widget, font)

    def set_color_of_widget(self, color, widget_name, panel_name):
        widget = self.get_widget_by_names(widget_name=widget_name, panel_name=panel_name)
        if widget is not None:
            widget.wx_widget.set_style_of_widget(widget, color)

#
# Threading class related #
class WorkerThreadResultEvent(wx.PyEvent):
    def __init__(self, data, wx_id):
        wx.PyEvent.__init__(self)
        self.SetEventType(wx_id)
        self.data = data


class WorkerThread(Thread):
    def __init__(self, func, parent, wx_id, run_once=True, sleep_time=0.2, args=None, call_event=False):
        Thread.__init__(self)
        self.func = func
        self.parent = parent
        self.run_once = run_once
        self.wx_id = wx_id
        self.sleep_time = sleep_time
        self.args = args
        self.call_event = call_event

        self.daemon = True
        self.running = True
        self.start()

    def run(self):
        if self.run_once:
            if self.args is not None:
                response = self.func(self.args)
            else:
                response = self.func()

            self.running = False
            if self.call_event:
                wx.PostEvent(self.parent, WorkerThreadResultEvent(response, self.wx_id))

        else:
            while self.running:
                if self.args is not None:
                    response = self.func(self.args)
                else:
                    response = self.func()
                if self.call_event:
                    wx.PostEvent(self.parent, WorkerThreadResultEvent(response, self.wx_id))
                time.sleep(self.sleep_time)

    def get_wx_id(self):
        return self.wx_id

    def kill(self):
        self.running = False

    def is_stopped(self) -> bool:
        return not self.isAlive()


#
# Monitor main thread process #
@dataclass
class ProcessInfo:
    main_name: str = sys.argv[0]
    process_name: str = ""
    pid: int = 0
    fps: float = ""
    perf_counter: int = 0
    refresh_rates: np.array = np.zeros(20)
    uptime: str = ""
    cpu_in_use: str = ""
    time_on_cpu: str = ""
    no_of_threads: str = ""
    memory_in_use: str = ""
    memory_usage: str = ""


def monitor_app_resources__init(frame) -> None:
    frame.process_info.perf_counter = time.perf_counter_ns()

    attrs = ('name', 'cmdline', 'pid', 'create_time', 'cpu_percent', 'cpu_times', 'num_threads', 'memory_percent')
    for proc in psutil.process_iter(attrs=attrs):
        if 'python' in proc.info['name']:
            if (cl := proc.info['cmdline']) is not None and len(cl) > 0 and frame.process_info.main_name in cl[-1]:
                frame.process_info.process_name = cl[-1]
                frame.process_info.pid = proc.info['pid']
                frame.process_info.uptime = f'{datetime.timedelta(seconds=time.time() - psutil.boot_time())}'
                frame.process_info.time_on_cpu = "{:}".format(
                    datetime.timedelta(
                        seconds=proc.info["cpu_times"].user - proc.info["cpu_times"].user
                    )
                )
                frame.process_info.no_of_threads = f'{proc.info["num_threads"]}',
                frame.process_info.memory_in_use = f'{(mem := proc.info["memory_percent"]):.3f}%',
                frame.process_info.memory_usage = f'{psutil.virtual_memory().total*(mem/100) / (1024**3):_.3f} GiB',

    frame.init_thread_worker(
        worker_id=wx.NewIdRef(), run_func=monitor_app_resources__loop_backend,
        args=frame, callback_func=None, run_once=False
    )


def monitor_app_resources__loop_frontend(frame) -> None:
    t_now = time.perf_counter_ns()
    dt = t_now - frame.process_info.perf_counter
    frame.process_info.refresh_rates[0] = dt
    frame.process_info.refresh_rates = np.roll(frame.process_info.refresh_rates, -1)
    frame.process_info.perf_counter = t_now

    dt = max(0.00001, frame.process_info.refresh_rates.mean() * 1e-9)
    fps_str = f"Refresh rate: {1/dt:.1f} [Hz]  |   "
    key_words = ["CPU in use", "Time on CPU", "No of threads", "Memory in use", "Memory usage"]
    values = [
        frame.process_info.cpu_in_use, frame.process_info.time_on_cpu, frame.process_info.no_of_threads,
        frame.process_info.memory_in_use, frame.process_info.memory_usage
    ]
    fps_str += "   ,  ".join([f"{key} = {values[i]}" for i, key in enumerate(key_words)])
    frame.monitor_textbox.SetValue(fps_str)


def monitor_app_resources__loop_backend(frame) -> None:
    process = psutil.Process(frame.process_info.pid)
    frame.process_info.uptime = f'{datetime.timedelta(seconds=time.time() - psutil.boot_time())}'
    frame.process_info.time_on_cpu = "{:}".format(
        datetime.timedelta(
            seconds=time.time() - process.cpu_times().user
        )
    )
    frame.process_info.cpu_in_use = f'{process.cpu_percent()}%'
    frame.process_info.no_of_threads = f'{process.num_threads():d}'
    frame.process_info.memory_in_use = f'{(mem := process.memory_percent()):.3f}%'
    frame.process_info.memory_usage = f'{psutil.virtual_memory().total * (mem / 100) / (1024 ** 3):_.3f} GiB'
    time.sleep(1)


#
#  Mouse click info, for deciding occurrence of double click
@dataclass()
class MouseDoubleClick:
    widget_name: str = ""
    time_of_last_click: int = 0
    time_limit: int = 400 * 1e6  # Convert to ms

    def double_clicked(self, widget_name: str = '') -> bool:
        t_now = time.perf_counter_ns()
        if widget_name == self.widget_name:
            if t_now - self.time_of_last_click < self.time_limit:
                self.time_of_last_click = t_now
                return True
        else:
            self.widget_name = widget_name
        self.time_of_last_click = t_now
        return False

    def reset(self):
        self.widget_name = ''
