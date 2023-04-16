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

        self.main_frame.add_timer(interval=10)

    def post_init(self):
        print("\n-- POST Initiation of Master --\n")

    def idle_function(self):
        self.update_ctrl_widget__state()
        self.update_ctrl_widget_alarm()
        self.update_ctrl_widget_rpm_and_current()

        self.update_ctrl_widget__dcdc()
        self.update_ctrl_widget__rotation()
        self.update_ctrl_widget__hydraulics()

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

    def update_ctrl_widget_rpm_and_current(self):
        name, panel = 'ctrl_1_0', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        if not widget.motor_enabled:
            widget.SetMotorEnable(True)

        widget.SetRpmValue(self.test_flag__run_rpm)
        if self.test_flag__run_rpm >= 1.0:
            self.test_flag__run_rpm = 0
        else:
            self.test_flag__run_rpm += 0.009

        widget.SetTorqueValue(self.test_flag__run_torque)
        if self.test_flag__run_torque >= 1.0:
            self.test_flag__run_torque = 0
        else:
            self.test_flag__run_torque += 0.007

        # print("Setting new Rpm and Torque values: ", self.test_flag__run_rpm, self.test_flag__run_torque)
        # self.main_frame.Layout()

    #
    def update_ctrl_widget__dcdc(self):
        name, panel = 'dcdc_display', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        # print(" -> widget: ", widget, widget.dcdc_enabled, widget.current_value, widget.voltage_value)
        if not widget.dcdc_enabled:
            widget.SetDcdcEnable(enable=True)
            new_val = 0
            widget.SetCurrentValueNormalized(value=new_val)

        else:
            new_val = widget.current_value + 0.01
            if new_val > 1.0:
                widget.SetDcdcEnable(enable=False)
                return
            widget.SetCurrentValueNormalized(value=new_val)

            real_current = new_val * 200 / 48 * 1000
            widget.SetCurrentValue(value=real_current)

            # Voltage
            new_val = widget.voltage_value + 0.02
            if new_val > 1.0:
                new_val = 0
            widget.SetVoltageValueNormalized(value=new_val)

            real_current = new_val * 350
            widget.SetVoltageValue(value=real_current)

    def update_ctrl_widget__rotation(self):
        name, panel = 'rotational_display', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        if not widget.widget_enabled:
            widget.SetWidgetEnable(enable=True)
            new_val = 0
            widget.SetRotationValues(value=new_val)

        else:
            new_val = widget.r_value + 0.01
            # print(f'new rot value: {new_val:.3f} rad |  {new_val*180/np.pi:.3f} deg')
            if new_val >= 2*np.pi:
                widget.SetWidgetEnable(enable=False)
                return

            real_val = new_val * (880 + 14*380 + 210) / 2/np.pi
            widget.SetRotationValues(value=new_val, real_value=real_val, setpoint=380*5)

    def update_ctrl_widget__hydraulics(self):
        name, panel = 'hydraulic_display', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        if not widget.widget_enabled:
            widget.SetWidgetEnable(enable=True)
            new_val = 0

            p_min = 17
            p_max = 150
            p_real = (p_max - p_min) * new_val + p_min
            # widget.SetPressureValues(animation_value=new_val, value=0.3)
            widget.SetPressureValues(animation_value=new_val, real_value=p_real, value=new_val)
            widget.SetSovValues(sov1_value=True, sov2_value=True)

        else:
            new_val = widget.p_animation_value + 0.01

            p_min = 17
            p_max = 150
            p_real = (p_max - p_min) * new_val + p_min

            if new_val > 0.0:
                if widget.sov1_open:
                    widget.SetSovValues(sov1_value=False, sov2_value=True)
            if new_val >= 2/3:
                if widget.sov2_open:
                    widget.SetSovValues(sov1_value=False, sov2_value=False)

            # print(f'new rot value: {new_val:.3f} rad |  {new_val*180/np.pi:.3f} deg')
            if new_val >= 1:
                widget.SetWidgetEnable(enable=False)
                return

            # real_val = 17.8
            widget.SetPressureValues(animation_value=new_val, real_value=p_real, value=new_val)