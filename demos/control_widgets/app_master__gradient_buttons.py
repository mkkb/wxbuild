import wx

import wxbuild.master_abstract as master
import wxbuild.components.styles_colors as wxcolors

import numpy as np
import time


class GradientButtonMaster(master.Master):
    def __init__(self, main_frame):
        self.main_frame = main_frame
        print(" master initiation..........................................")

        self.main_frame.add_idle_function(self.idle_function)

        self.test_flag__drivestate = 0
        self.test_flag__alarm = 0
        self.test_flag__run_rpm = 0
        self.test_flag__run_torque = 0

    def post_init(self):
        print("\n-- POST Initiation of Master --\n")

    def idle_function(self):
        self.update_ctrl_widget__state()
        self.update_ctrl_widget_alarm()

    def handle_user_event(self, event_type, name, panel):
        print(f" HANDLING USER EVENT:::  type: {event_type} | name: {name} | panel: {panel}")

        if name == 'ctrl_0_0':
            self.update_ctrl_widget__state()

    def update_ctrl_widget__state(self):
        name, panel = 'ctrl_0_0', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)
        possible_states = widget.GetPossibleStateNames()
        n_states = len(possible_states)

        widget.SetState(self.test_flag__drivestate)
        if self.test_flag__drivestate >= 2 ** n_states - 1:
            self.test_flag__drivestate = 0
        else:
            for i in range(n_states):
                if 2 ** i & self.test_flag__drivestate:
                    pass
                else:
                    self.test_flag__drivestate += 2 ** i
                    break
        # print("   next state value will be = ", self.test_flag)

    def update_ctrl_widget_alarm(self):
        name, panel = 'ctrl_2_0', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)
        possible_states = widget.GetPossibleStateNames()
        n_states = len(possible_states)
        # print(" -> widget.state_names : ", possible_states)
        # print(" -> widget.state_values: ", widget.GetPossibleStateValues())
        # current_state = widget.GetState()
        # print("   current_state = ", current_state, " | ", self.test_flag,
        #       " || ", self.test_flag & 2 ** n_states, n_states, 2 ** n_states)

        widget.SetState(self.test_flag__alarm)
        if self.test_flag__alarm >= 2 ** n_states - 1:
            self.test_flag__alarm = 0
        else:
            for i in range(n_states):
                if 2 ** i & self.test_flag__alarm:
                    pass
                else:
                    self.test_flag__alarm += 2 ** i
                    break
        # print("   next state value will be = ", self.test_flag)
