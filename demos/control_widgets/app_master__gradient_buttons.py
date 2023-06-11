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

        self.widget_value_dict = {}

    def post_init(self):
        print("\n-- POST Initiation of Master --\n")

    def idle_function(self):
        self.update_ctrl_widget__state()
        self.update_ctrl_widget_alarm()
        self.update_ctrl_widget_rpm_and_current()

        self.update_ctrl_widget__dcdc()
        self.update_ctrl_widget__rotation()
        self.update_ctrl_widget__hydraulics()
        self.update_ctrl_widget__sensorbaord_temps()

        self.update_ctrl_widget__custom_widget_1()
        self.update_ctrl_widget__custom_widget_2()
        self.update_ctrl_widget__custom_widget_3()

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
        if not widget.widget_enable:
            widget.SetWidgetEnable(enable=True)
            new_val = 0
            widget.SetCurrentValueNormalized(value=new_val)

        else:
            new_val = widget.current_value + 0.01
            if new_val > 1.0:
                widget.SetWidgetEnable(enable=False)
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

    #
    def update_ctrl_widget__sensorbaord_temps(self):
        name, panel = 'sensorboard_temperature_states', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        # print(" -> widget: ", widget, widget.dcdc_enabled, widget.current_value, widget.voltage_value)
        if not widget.widget_enable:
            widget.SetWidgetEnable(enable=True)
            new_val = 0
            widget.SetTemperatures(
                val_a=new_val, val_b=new_val, val_c=new_val, val_d=new_val, val_e=new_val, val_f=new_val)

        else:
            vals = []
            real_vals = []
            for w_name in 'abcdef':
                val_increment = np.random.randint(1, 20) / 100
                w_name = f'temperature_{w_name}'
                new_val = getattr(widget, w_name) + val_increment
                if new_val > 1.0:
                    widget.SetWidgetEnable(enable=False)
                    return

                new_real_value = new_val*120 - 5

                vals.append(new_val)
                real_vals.append(new_real_value)

            widget.SetTemperatures(*vals)
            widget.SetTemperatureRealValues(*real_vals)

    def update_ctrl_widget__custom_widget_1(self):
        name, panel = 'custom_display_1', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        text_labels = [
            'AccX',
            'AccY',
            'AccZ',
        ]
        text_value_format = [
            'X G',
            'X G',
            'X G',
        ]
        min_val = -4
        max_val = 4
        val_range = max_val - min_val

        # Simulate accelerometer axis -> Initialization
        if len(widget.text_labels) == 0:
            for i in range(6):
                x = (i // 3) * 0.68
                y = (i % 3) * 0.33
                #
                if i < 3:
                    label = text_labels[i]
                    self.widget_value_dict[text_labels[i]] = 0
                else:
                    label = f'{text_value_format[i%3].replace("X", "0")}'
                widget.edit_text_attributes(index=i, pos_x=x, pos_y=y)
                widget.edit_text_label(index=i, text=label)
                #
                if i < 3:
                    widget.edit_bar_attributes(
                        index=i, pos_x=0.25, pos_y=y, size_w=0.4, size_h=0.2, alignment=0, setpoints=(0.5,))
                    widget.edit_bar_value(index=i, bar_value=0)

        # Simulate accelerometer axis -> looping
        else:
            if not widget.widget_enable:
                # pass
                widget.SetWidgetEnable(enable=True)
            else:
                for i in range(3, 6):
                    old_val = self.widget_value_dict[text_labels[i%3]]
                    val_increment = np.random.randint(1, 200) / 500
                    new_val = old_val + val_increment
                    if new_val >= max_val:
                        new_val = min_val
                        widget.SetWidgetEnable(enable=False)

                    self.widget_value_dict[text_labels[i % 3]] = new_val
                    label = f'{text_value_format[i % 3].replace("X", f"{new_val:0.2f}")}'
                    widget.edit_text_label(index=i, text=label)
                    normalized_value = (new_val - min_val)/val_range
                    # print(" -> ", new_val, min_val, val_range, normalized_value)
                    widget.edit_bar_value(index=i%3, bar_value=normalized_value)

    def update_ctrl_widget__custom_widget_2(self):
        name, panel = 'custom_display_2', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        text_labels = [
            'AngX',
            'AngY',
            'AngZ',
        ]
        text_value_format = [
            'X°',
            'X°',
            'X°',
        ]
        min_val = -180
        max_val = 180
        val_range = max_val - min_val

        # Simulate accelerometer axis -> Initialization
        if len(widget.text_labels) == 0:
            new_size = wx.Size(70, 27)
            widget.SetSize(new_size)
            widget.SetInitialSize(new_size)
            self.main_frame.Layout()
            for i in range(6):
                x = (i // 3) * 0.7
                y = (i % 3) * 0.33
                #
                if i < 3:
                    label = text_labels[i]
                    self.widget_value_dict[text_labels[i]] = 0
                else:
                    label = f'{text_value_format[i % 3].replace("X", "0")}'
                widget.edit_text_attributes(index=i, pos_x=x, pos_y=y)
                widget.edit_text_label(index=i, text=label)
                #
                if i < 3:
                    widget.edit_bar_attributes(
                        index=i, pos_x=0.32, pos_y=y + 0.04, size_w=0.35, size_h=0.15, alignment=0)
                    widget.edit_bar_value(index=i, bar_value=0.2)

        # Simulate accelerometer axis -> looping
        else:
            if not widget.widget_enable:
                # pass
                widget.SetWidgetEnable(enable=True)
            else:
                for i in range(3, 6):
                    old_val = self.widget_value_dict[text_labels[i % 3]]
                    val_increment = np.random.randint(100, 2000) / 100
                    new_val = old_val + val_increment
                    if new_val >= max_val:
                        new_val = min_val
                        widget.SetWidgetEnable(enable=False)

                    self.widget_value_dict[text_labels[i % 3]] = new_val
                    label = f'{text_value_format[i % 3].replace("X", f"{new_val:0.1f}")}'
                    widget.edit_text_label(index=i, text=label)
                    normalized_value = (new_val - min_val) / val_range
                    # print(" -> ", new_val, min_val, val_range, normalized_value)
                    widget.edit_bar_value(index=i % 3, bar_value=normalized_value)

    def update_ctrl_widget__custom_widget_3(self):
        name, panel = 'custom_display_3', 'motorctrls'
        widget = self.main_frame.get_widget_by_names(widget_name=name, panel_name=panel)

        text_value_format = 'Vpp=X , CCL=Y'
        min_val_x = 0
        max_val_x = 6000
        # val_range_x = max_val_x - min_val_x
        min_val_y = 0.0
        max_val_y = 4.99999
        val_range_y = max_val_y - min_val_y

        # Simulate accelerometer axis -> Initialization
        if len(widget.text_labels) == 0:
            new_size = wx.Size(90, 27)
            widget.SetSize(new_size)
            widget.SetInitialSize(new_size)
            self.main_frame.Layout()

            x = 0
            y = 0.67
            #
            val_x = np.zeros(12, dtype=np.float32) + 4.999
            val_y = 99999
            label = f'{text_value_format.replace("X", f"{val_x[-1]:2<.3f}").replace("Y", f"{val_y:<3d}")}'
            widget.edit_text_attributes(index=0, pos_x=x, pos_y=y)
            widget.edit_text_label(index=0, text=label)

            x_val_label = 'ccl_count'
            self.widget_value_dict[x_val_label] = val_y

            x_val_label = 'ccl_vpp'
            self.widget_value_dict[x_val_label] = val_x

            widget.edit_graph_attributes(
                index=0, pos_x=0, pos_y=0, size_w=1, size_h=0.66)

        # Simulate accelerometer axis -> looping
        else:
            if not widget.widget_enable:
                widget.SetWidgetEnable(enable=True)
                # pass
            else:
                x_val_label = 'ccl_count'
                old_val_x = self.widget_value_dict[x_val_label]
                val_increment_x = np.random.randint(0, 2)
                new_val_x = old_val_x + val_increment_x
                if new_val_x >= max_val_x:
                    new_val_x = min_val_x
                    widget.SetWidgetEnable(enable=False)
                self.widget_value_dict[x_val_label] = new_val_x

                y_val_label = 'ccl_vpp'
                amp = 2  # np.random.randint(1.2, 2.49)
                offset = 2.49
                if int(time.time()) % 3 == 0:
                    amp = 0
                    offset = max_val_y - 0.05

                t = time.time() + np.arange(128) / 128
                f = 0.1
                new_val = amp*np.sin(2*np.pi*t * f) + offset
                new_val[new_val > max_val_y] = max_val_y
                new_val[new_val < min_val_y] = min_val_y

                label = f'{text_value_format.replace("X", f"{new_val[-1]:2<.3f}").replace("Y", f"{new_val_x:<3d}")}'

                new_val /= val_range_y
                new_val = new_val.astype(np.float32)

                widget.edit_graph_data(index=0, data=new_val[-1:])
                widget.edit_text_label(index=0, text=label)
