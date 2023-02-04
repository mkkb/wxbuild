import time
from dataclasses import dataclass
import wx

import sys
from wxbuild.vispy_fixes import ptime
sys.modules["vispy.util.ptime"] = ptime
from wxbuild.vispy_fixes import line
sys.modules["vispy.visuals.line"] = line

from vispy import scene
import numpy as np
import logging
logger = logging.getLogger('wx_log')

from wxbuild.components.styles_colors import ColorsCyclic
import wxbuild.components.custom_widgets.gradientbutton as wxgb


PlotColors = ColorsCyclic()


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_flags: int = wx.EXPAND | wx.ALL
    sizer_proportion: float = 1
    sizer_border: int = 0
    sizer_direction: str = 'horizontal'
    shape: tuple = (1, 1)
    size: tuple = (500, 500)
    background_color: tuple = wx.WHITE


@dataclass
class MousePointerInfo:
    label: str = ""
    x_unit: str = ""
    y_unit: str = ""
    print_notation: str = "0.1f"
    stats_mean: float = 0.0
    stats_std: float = 0.0
    stats_max: float = 0.0
    stats_min: float = 0.0
    stats_local_mean: float = 0.0
    stats_local_std: float = 0.0
    stats_local_max: float = 0.0
    stats_local_min: float = 0.0
    point_x: float = 0.0
    point_y: float = 0.0


@dataclass
class VispyLine:
    n_size: int = 32
    n_size_init: int = n_size
    return_nan_data: bool = False
    n_lines: int = 1
    line_index: int = 0
    view_index: int = 0
    x_data: np.ndarray = np.arange(n_size, dtype=np.float32)
    x_unit: str = ""
    y_data: np.ndarray = np.arange(n_size, dtype=np.float32)
    y_unit: str = ""
    print_notation: str = "0.1f"
    vispy_line_start_index: int = n_size * line_index + line_index
    vispy_line_end_index: int = vispy_line_start_index + n_size + 1
    color = PlotColors.get_color_by_index(0)
    update_color = False
    label: str = ""
    description: str = ""
    split_view_col_index: int = 0
    split_view_row_index: int = 0
    show: bool = True
    initialized: bool = False
    normalize: bool = False
    stats_marker_x: float = 0.0
    stats_marker_y: float = 0.0
    stats_mean: float = 0.0
    stats_std: float = 0.0
    stats_max: float = 0.0
    stats_min: float = 0.0
    stats_local_width: int = 10
    local_x_value: int = 16
    stats_local_mean: float = 0.0
    stats_local_std: float = 0.0
    stats_local_max: float = 0.0
    stats_local_min: float = 0.0
    #
    normalize_offset_y: float = 0.0
    normalize_scaler_y: float = 0.0
    normalize_offset_x: float = 0.0
    normalize_scaler_x: float = 0.0

    def set_line_size(self, n_size):
        self.n_size = n_size
        self.n_size_init = n_size
        self.x_data = np.arange(n_size, dtype=np.float32)
        self.y_data = np.zeros(n_size, dtype=np.float32)
        self.vispy_line_start_index = n_size * self.line_index + self.line_index
        self.vispy_line_end_index = self.vispy_line_start_index + n_size # + 1

    def get_data(self):
        # logger.info(" get_data", self.show, self.normalize, " | ", self.label, self.description, " | ", self.return_nan_data, " | ", self.n_size, self.n_size_init)
        if not self.show:
            # logger.info("  -* not showing data, returning nans")
            pos = np.zeros(shape=(self.n_size_init, 2), dtype=np.float32)
            pos[self.n_size:, :] = np.nan
            return pos

        if self.return_nan_data:
            pos = np.zeros(shape=(self.n_size_init, 2), dtype=np.float32)
            pos[self.n_size:, :] = np.nan
        else:
            pos = np.zeros(shape=(self.n_size, 2), dtype=np.float32)

        if self.normalize:
            pos[: self.n_size, 0] = self.get_x_data_split_view()
            pos[: self.n_size, 1] = self.get_y_data_split_view()
            # logger.info("  -* getting normalized data: ", self.label, " | ", self.split_view_row_index, self.split_view_col_index)
            # logger.info("  -* -> x : ", np.amin(self.get_x_data_split_view()[: self.n_size]), np.amax(self.get_x_data_split_view()[: self.n_size]) , self.n_size,
            #       "  -* || ", np.amin(self.get_x_data()[: self.n_size]), np.amax(self.get_x_data()[: self.n_size]))
            # logger.info("  -* -> y : ", np.amin(self.get_y_data_split_view()[: self.n_size]), np.amax(self.get_y_data_split_view()[: self.n_size]) , self.n_size,
            #       "  -* || ", np.amin(self.get_y_data()[: self.n_size]), np.amax(self.get_y_data()[: self.n_size]))
        else:
            pos[: self.n_size, 0] = self.x_data[:self.n_size]
            pos[: self.n_size, 1] = self.y_data[:self.n_size]
            # logger.info("  -* getting plain data", self.x_data[:self.n_size].mean(), self.y_data[:self.n_size].mean())

        if self.return_nan_data:
            self.return_nan_data = False
            # logger.info("  -* returning (also nan data):: ", pos.shape, np.amin(pos[:, 0]), np.amax(pos[:, 0]), np.amin(pos[:, 1]), np.amax(pos[:, 1]))
            # logger.info(pos)
            return pos, self.vispy_line_start_index, self.vispy_line_start_index + self.n_size_init
        else:
            return pos, self.vispy_line_start_index, self.vispy_line_end_index

    def get_y_data(self):
        y = self.y_data[:]
        if self.n_size_init > self.n_size:
            y[self.n_size: self.n_size_init, :] = np.nan
        return y

    def get_x_data(self):
        x = self.x_data[:]
        if self.n_size_init > self.n_size:
            x[self.n_size: self.n_size_init, :] = np.nan
        return x

    def get_color_single_point(self):
        c = self.color
        r, g, b = c.Red(), c.Green(), c.Blue()
        color_arr = np.zeros(shape=(1, 4), dtype=np.float32)
        color_arr[:, :] = np.array([r, g, b, 255], dtype=np.float32) / 255
        # logger.info("  vispy_line  new_color:: ", r, g, b, " || ", color_arr)
        self.update_color = False
        return color_arr

    def get_color_data(self):
        logger.info(" - getting color data from line:: ", self.label, self.n_size, self.n_size_init)
        c = self.color
        r, g, b = c.Red(), c.Green(), c.Blue()
        color_arr = np.zeros(shape=(self.n_size_init, 4), dtype=np.float32)
        color_arr[:, :] = np.array([r, g, b, 255], dtype=np.float32) / 255
        self.update_color = False
        return color_arr

    def get_x_data_split_view(self):
        # logger.info("  -*  get_x_data_split_view:: ", self.normalize_offset_x, self.normalize_scaler_x, self.split_view_row_index)
        normalized_data = self.x_data[:self.n_size] - self.normalize_offset_x
        normalized_data = normalized_data * self.normalize_scaler_x + 0.025 + self.split_view_row_index
        # logger.info("  -*  get_x_data_split_view:: ", normalized_data)
        return normalized_data

    def get_y_data_split_view(self):
        # logger.info("  -*  get_y_data_split_view:: ", self.normalize_offset_y, self.normalize_scaler_y, self.split_view_col_index)
        normalized_data = self.y_data[:self.n_size] - self.normalize_offset_y
        normalized_data = normalized_data * self.normalize_scaler_y + 0.025 + self.split_view_col_index
        # logger.info("  -*  get_y_data_split_view:: ", normalized_data)
        return normalized_data

    def set_data(self, x: np.ndarray, y: np.ndarray):
        self.initialized = True
        if x.size != self.n_size:
            self.n_size = x.size
            self._reset_vispy_line_indices()
            self._reset_normalization_parameters()
        #
        self.x_data[:self.n_size] = x[:self.n_size]
        self.y_data[:self.n_size] = y[:self.n_size]
        #
        self._calculate_stats()
        self._calculate_local_stats_from_x()

    def set_y_data(self, y: np.ndarray):
        self.initialized = True
        if y.size != self.n_size:
            self.n_size = y.size
            new_size = True
        else:
            new_size = False
        self.y_data[:self.n_size] = y[:self.n_size]

        if new_size:
            # logger.info(" set_y_data:: y.size != self.n_size")
            self._reset_vispy_line_indices()
            self._reset_normalization_parameters()
        else:
            self.normalize_offset_y = np.amin(self.y_data[:self.n_size])
            amax = np.amax(self.y_data[:self.n_size] - self.normalize_offset_y)
            if amax > 0:
                self.normalize_scaler_y = 1 / amax * 0.95
            else:
                self.normalize_scaler_y = 1
            # logger.info(" set_y_data:: y.size == self.n_size  || ", self.normalize_offset_y, self.normalize_scaler_y)

        self._calculate_stats()
        self._calculate_local_stats_from_x()
        # logger.info(" set_y_data:: ", y.shape, " || ", np.amax(y), np.amin(y), self.n_size)

    def set_x_data(self, x: np.ndarray):
        self.initialized = True
        if x.size != self.n_size:
            self.n_size = x.size
            new_size = True
        else:
            new_size = False
        self.x_data[:self.n_size] = x[:self.n_size]

        if new_size:
            self.n_size = x.size
            self._reset_vispy_line_indices()
            self._reset_normalization_parameters()
        else:
            self.normalize_offset_x = np.amin(x[:self.n_size])
            amax = np.amax(self.x_data[:self.n_size] - self.normalize_offset_x)
            if amax > 0:
                self.normalize_scaler_x = 1 / amax * 0.95
            else:
                self.normalize_scaler_x = 1
        # logger.info(" recalculating normalization numbers:", self.normalize_offset_x, self.normalize_scaler_x, " | ", self.label, self.split_view_row_index, self.split_view_col_index)
        #
        self._calculate_stats()
        self._calculate_local_stats_from_x()
        # logger.info(" set_x_data:: ", x.shape, " || ", np.amin(x), np.amax(x), self.n_size)

    def set_color(self, color):
        self.color = color
        self.update_color = True

    def set_label(self, label):
        self.label = label

    def set_description(self, description):
        self.description = description

    def get_description(self):
        return self.description

    def set_units(self, x_unit: str, y_unit: str):
        self.x_unit = x_unit
        self.y_unit = y_unit

    def get_units(self):
        return self.x_unit, self.y_unit

    def set_show_mode(self, show: bool, normalize: bool):
        self.show = show
        self.normalize = normalize

    def set_split_view_col_and_row(self, col, row):
        self.split_view_col_index = col
        self.split_view_row_index = row

    def set_split_view_coordinate(self, split_view_col_index, split_view_row_index):
        self.split_view_col_index = split_view_col_index
        self.split_view_row_index = split_view_row_index

    def get_xarg_by_split_data_position(self, x_value):
        normalized_data = self.x_data - np.amin(self.x_data)
        normalized_data = normalized_data / np.amax(normalized_data) * 0.95 + 0.025 + self.split_view_row_index
        return np.argmin(np.abs(normalized_data - x_value))

    def get_xarg_by_data_position(self, x_value):
        return np.argmin(np.abs(self.x_data - x_value))

    def get_stats(self):
        return self.stats_mean, self.stats_std, self.stats_max, self.stats_min

    def get_local_stats(self):
        return self.stats_local_mean, self.stats_local_std, self.stats_local_max, self.stats_local_min

    def get_exact_point_stats(self):
        x_arg = self.local_x_value
        return self.x_data[x_arg], self.y_data[x_arg]

    def _calculate_stats(self):
        self.stats_mean = self.y_data.mean()
        self.stats_std = self.y_data.std()
        self.stats_max = np.max(self.y_data)
        self.stats_min = np.min(self.y_data)

    def set_local_x_value_from_normalized_x(self, x_normalized):
        x = x_normalized - 0.025 - self.split_view_row_index
        x_arg = max(min(int(x / 0.95 * self.n_size), self.n_size-1), 0)
        self.local_x_value = x_arg
        self._calculate_local_stats_from_x()
        # logger.info("\nset_local_x_value_from_normalized_x: ", self.label, self.split_view_row_index, self.normalize_scaler_x)
        # logger.info("   - ", x_normalized, x,  x_arg, "  |  ", self.n_size)
        # logger.info("  ")
        # if self.normalize_scaler_x > 0:
        #     x /= self.normalize_scaler_x
        #     x += self.normalize_offset_x
        #
        #     self.local_x_value = x
        #     self._calculate_local_stats_from_x()
        #     pass

    def set_local_x_value(self, x_value):
        self.local_x_value = x_value
        self._calculate_local_stats_from_x()

    def set_stats_local_width(self, stats_local_width):
        self.stats_local_width = stats_local_width
        self._calculate_local_stats_from_x()

    def _calculate_local_stats_from_x(self):
        # x_arg = np.argmin(np.abs(self.x_data - self.local_x_value))
        x_arg = self.local_x_value
        w = self.stats_local_width
        index_min = max(0, x_arg - w//2)
        index_max = min(self.n_size, x_arg + w // 2)

        # logger.info("\n local x_value::: ", self.label, x_arg, w)
        # logger.info("  -- ", index_min, index_max)
        if index_max - index_min > 1:
            self.stats_local_mean = self.y_data[index_min: index_max].mean()
            self.stats_local_std = self.y_data[index_min: index_max].std()
            self.stats_local_max = np.max(self.y_data[index_min: index_max])
            self.stats_local_min = np.min(self.y_data[index_min: index_max])

    def _calculate_local_stats_from_y(self, y):
        y_arg = np.argmin(np.abs(self.y_data - y))
        w = self.stats_local_width
        index_min = max(0, y_arg - w // 2)
        index_max = min(self.y_data.size, y_arg + w // 2)

        if index_max - index_min > 1:
            self.stats_local_mean = self.y_data[index_min: index_max].mean()
            self.stats_local_std = self.y_data[index_min: index_max].std()
            self.stats_local_max = np.max(self.y_data[index_min: index_max])
            self.stats_local_min = np.min(self.y_data[index_min: index_max])

    def _reset_vispy_line_indices(self):
        self.vispy_line_start_index = self.n_size_init * self.line_index + self.line_index
        self.vispy_line_end_index = self.vispy_line_start_index + self.n_size # + 1
        self.return_nan_data = True

    def _reset_normalization_parameters(self):
        # logger.info('.. reseting noramilzation params:: ', self.label, self.n_size, self.n_size_init)
        self.normalize_offset_x = np.amin(self.x_data[:self.n_size])
        amax = np.amax(self.x_data[:self.n_size] - self.normalize_offset_x)
        if amax > 0:
            self.normalize_scaler_x = 1 / amax * 0.95
        else:
            self.normalize_scaler_x = 1
        #
        # logger.info(" _reset_normalization_parameters  y_data:: ", self.y_data[:self.n_size])
        self.normalize_offset_y = np.amin(self.y_data[:self.n_size])
        amax = np.amax(self.y_data[:self.n_size] - self.normalize_offset_y)
        if amax > 0:
            self.normalize_scaler_y = 1 / amax * 0.95
        else:
            self.normalize_scaler_y = 1


class VispyCanvas(scene.SceneCanvas):
    def __init__(self, *args, **kwargs):
        scene.SceneCanvas.__init__(self, *args, **kwargs)

    @staticmethod
    def get_view_rect(view):
        attrib_names = ["width", "height", "left", "right", "bottom", "top"]
        attrib_list = [None, ] * len(attrib_names)

        for i, attrib in enumerate(attrib_names):
            if hasattr(view.camera.rect, attrib):
                attrib_list[i] = getattr(view.camera.rect, attrib)

        return attrib_list

    def zoom_in_x(self, view, margin=0.0):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = l + w / 2
        new_w = w / 2
        y_lim = (b, t)
        x_lim = (center - new_w, center + new_w)
        view.camera.set_range(x_lim, y_lim, margin=margin)

    def zoom_out_x(self, view, margin=0.0):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = l + w / 2
        new_w = w * 2
        y_lim = (b, t)
        x_lim = (center - new_w, center + new_w)
        view.camera.set_range(x_lim, y_lim, margin=margin)

    def zoom_in_y(self, view, margin=0.0):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = b + h / 2
        new_h = h / 2
        y_lim = (center - new_h, center + new_h)
        x_lim = (b, t)
        view.camera.set_range(x_lim, y_lim, margin=margin)

    def zoom_out_y(self, view, margin=0.0):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = b + h / 2
        new_h = h * 2
        y_lim = (center - new_h, center + new_h)
        x_lim = (b, t)
        view.camera.set_range(x_lim, y_lim, margin=margin)

    def zoom_all_out_x(self, view, lims=(0.0, 0.1)):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        y_lim = (b, t)
        x_lim = lims
        view.camera.set_range(x_lim, y_lim, margin=0.0)

    def zoom_all_out_y(self, view, lims=(0.0, 0.1)):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        y_lim = lims
        x_lim = (l, r)
        view.camera.set_range(x_lim, y_lim, margin=0.0)


class VispyPanel(wx.Panel):
    def __init__(self, parent, main_frame, **kwargs):
        self.dataclass = WxPanel
        self.main_frame = main_frame
        self.parent = parent
        if 'shape' in kwargs:
            self.plot_cols, self.plot_rows = kwargs.pop('shape')
        else:
            self.plot_cols, self.plot_rows = 1, 1

        wx.Panel.__init__(self, parent, **kwargs)

        self.show_legend_panel = False
        self.show_tooltip_panel = False
        self.legend_panels = []
        self.tooltip_panel = ToolTip(self, size=wx.Size(100, 200), pos=(20, 20))
        # self.tooltip_panel.SetBackgroundColour(wx.Colour("#aabbaa"))
        self.tooltip_panel.Hide()

        for i in range(self.plot_rows * self.plot_cols):
            panel_ = LegendPanel(self, size=wx.Size(100, 200), pos=(500 + 20*i, 40 + 5*i))
            self.legend_panels.append(panel_)
            panel_.Hide()

        self.N = 64
        self.data_info = []
        self.data_sets = {  # One set per viewbox
            # 0: [
            #     np.empty(shape=(1, 0, 2), dtype=np.float32),  # vertex coordinates
            #     np.empty(shape=(1, 0, 4), dtype=np.float32),  # vertex colors
            #     np.empty(shape=(1, 0, 2), dtype=np.float32),  # if a image
            # ],
        }
        self.selected_view_index = 0
        self.minimum_refresh_rate_ms = 100
        self.time_of_last_refresh = self.get_time_now_ms()
        self.pending_line_updates = []
        self.pointer_info__line_stats = MousePointerInfo()

        self.play = True
        self.play_color = (1, 0, 0, 1)
        self.pause_color = (1, 0, 0, 1)
        self.show_crosshair = False

        self.initialized = 0
        self.resized = False
        self.canvas = VispyCanvas(app='wx', parent=self, keys='interactive', bgcolor='black', size=kwargs['size'])
        grid = self.canvas.central_widget.add_grid(spacing=0)

        self.mouse_over_plot = 0
        self.mouse_dragging = False
        self.mouse_moved = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_x_absolute = 0
        self.mouse_y_absolute = 0
        self.mousemove_callback = None
        self.mouseclick_callback = None
        #
        self.view_boxes = []
        self.line_labels = {}
        self.lines = {}
        self.line_crosshairs = []
        self.ax_lines = []
        self.vertical_lines = []
        self.horizontal_lines = []
        #
        self.x_data_min = []
        self.x_data_max = []
        self.y_data_min = []
        self.y_data_max = []
        #
        self.x_axis = []
        self.y_axis = []
        self.gridlines = []

        for row in range(self.plot_rows):
            for col in range(self.plot_cols):
                view_box = grid.add_view(row=row, col=col, camera='panzoom', border_color='w')

                x_axis = scene.AxisWidget(orientation='top')
                x_axis.stretch = (1, 0.1)
                grid.add_widget(x_axis, row=row, col=col)
                x_axis.link_view(view_box)
                self.x_axis.append(x_axis)

                y_axis = scene.AxisWidget(orientation='right')
                y_axis.stretch = (0.1, 1)
                grid.add_widget(y_axis, row=row, col=col)
                y_axis.link_view(view_box)
                self.y_axis.append(y_axis)

                self.gridlines.append(scene.visuals.GridLines(color='w', parent=view_box.scene))
                self.view_boxes.append(view_box)
                self.x_data_min.append(99999999)
                self.x_data_max.append(-99999999)
                self.y_data_min.append(99999999)
                self.y_data_max.append(-99999999)

        self.adapt_canvas_size()
        self.canvas.show()
        self.Bind(wx.EVT_SIZE, self.on_repaint)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.canvas.events.key_press.connect(self.on_key_pressed)
        self.canvas.events.mouse_move.connect(self.on_mouse_moved)
        self.canvas.events.mouse_release.connect(self.on_mouse_released)
        self.canvas.events.mouse_press.connect(self.on_mouse_pressed)

    def post_init(self):
        from wxbuild.components.mainframe import Timer
        self.tooltip_timer = Timer(timeout_limit_ms=50, timeout_long_limit_ms=800)

    #
    def get_time_now_ms(self):
        return time.perf_counter_ns()//1e6

    def on_mouse_released(self, _):  # _ = event
        self.mouse_dragging = False

    def on_mouse_pressed(self, event):
        self.mouse_dragging = True
        self.hide_info_panels()

        if hasattr(self.mouseclick_callback, '__call__'):
            self.mouseclick_callback(event)

    def on_mouse_moved(self, event):
        if self.mouse_dragging:
            pass

        else:
            # Dirty fix to bug that fix a pan zoom problem that occurs when dragging outside the view
            if event._button is None:
                if len(event._buttons) > 0:
                    self.canvas._backend._vispy_mouse_data['buttons'] = []

        self.get_mouse_view_box_coordinates(event)

        self.mouse_moved = True
        if self.show_tooltip_panel:
            if self.tooltip_panel.IsShown():
                self.tooltip_panel.Hide()
            self.tooltip_timer.reset_timer()

        if hasattr(self.mousemove_callback, '__call__'):
            self.mousemove_callback(event)

    def on_key_pressed(self, event):
        if hasattr(event.key, 'name'):
            key_char = event.key.name
            if key_char in 'ASHZXCQWE':
                if key_char == 'H':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot)
                elif key_char == 'Z':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)
                elif key_char == 'X':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)
                elif key_char == 'C':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)
                elif key_char == 'Q':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)
                elif key_char == 'W':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)
                elif key_char == 'E':
                    self.reset_axis_limits(ax_index=self.mouse_over_plot, direction=-1)

    #
    def get_plot_index_from_mouse_coordinates(self, mouse_x, mouse_y):
        for i, view_box in enumerate(self.view_boxes):
            x0, x1 = view_box.pos[0], view_box.pos[0] + view_box.width
            y0, y1 = view_box.pos[1], view_box.pos[1] + view_box.height
            if mouse_x >= x0:
                if mouse_x <= x1:
                    if mouse_y >= y0:
                        if mouse_y <= y1:
                            self.mouse_over_plot = i
                            return
        self.mouse_over_plot = -1

    def get_mouse_view_box_coordinates(self, event):
        self.get_plot_index_from_mouse_coordinates(*event.pos)
        plot_index = self.mouse_over_plot
        self.mouse_x_absolute, self.mouse_y_absolute = event.pos

        view_box = self.view_boxes[plot_index]

        rect_x, rect_y = [getattr(view_box.rect, attrib) for attrib in ['right', 'top']]

        row, col = plot_index // self.plot_rows, plot_index % self.plot_cols
        mouse_x_vb, mouse_y_vb = self.mouse_x_absolute - col * rect_x, self.mouse_y_absolute - row*rect_y

        x_camera_rect_pos, y_camera_rect_pos = view_box.camera.rect.pos
        x_camera_rect_size, y_camera_rect_size = view_box.camera.rect.size

        normalized_x, normalized_y = mouse_x_vb / rect_x, 1 - mouse_y_vb / rect_y
        view_box_mouse_x = normalized_x * x_camera_rect_size + x_camera_rect_pos
        view_box_mouse_y = normalized_y * y_camera_rect_size + y_camera_rect_pos

        # # Get closest point on line to mouse
        if plot_index in self.data_sets:
            for l_indx, line in self.data_sets[plot_index].items():
                if line.initialized:
                    # logger.info(" is this a good line?", l_indx, line.label, " | ", line.split_view_row_index, int(view_box_mouse_x), " | ", line.split_view_col_index, int(view_box_mouse_y))
                    # logger.info("  -- ", view_box_mouse_x, int(view_box_mouse_x), view_box_mouse_y, int(view_box_mouse_y), " || ", line.split_view_row_index, line.split_view_col_index)
                    if line.split_view_row_index == int(view_box_mouse_x):
                        if line.split_view_col_index == int(view_box_mouse_y):
                            # logger.info(" Good line?? ", line.label, line.split_view_row_index, line.split_view_col_index, " || ", int(view_box_mouse_x), int(view_box_mouse_y))
                            line.set_local_x_value_from_normalized_x(view_box_mouse_x)

                            line_stats = line.get_stats()
                            line_local_stats = line.get_local_stats()
                            line_point_stats = line.get_exact_point_stats()

                            self.pointer_info__line_stats.stats_mean = line_stats[0]
                            self.pointer_info__line_stats.stats_std = line_stats[1]
                            self.pointer_info__line_stats.stats_max = line_stats[2]
                            self.pointer_info__line_stats.stats_min = line_stats[3]
                            self.pointer_info__line_stats.stats_local_mean = line_local_stats[0]
                            self.pointer_info__line_stats.stats_local_std = line_local_stats[1]
                            self.pointer_info__line_stats.stats_local_max = line_local_stats[2]
                            self.pointer_info__line_stats.stats_local_min = line_local_stats[3]
                            self.pointer_info__line_stats.point_x = line_point_stats[0]
                            self.pointer_info__line_stats.point_y = line_point_stats[1]
                            self.pointer_info__line_stats.label = line.label
                            self.pointer_info__line_stats.x_unit = line.x_unit
                            self.pointer_info__line_stats.y_unit = line.y_unit
                            self.pointer_info__line_stats.print_notation = line.print_notation

                            if self.show_tooltip_panel:
                                self.tooltip_panel.update_info(self.pointer_info__line_stats)
        # line_pos = self.lines[plot_index].pos
        # non_nans_mask = ~np.isnan(line_pos[:, 1]) & ~np.isnan(line_pos[:, 0])
        # x_ = line_pos[non_nans_mask, 0]
        # y_ = line_pos[non_nans_mask, 1]
        #
        # logger.info(" shape line_pos:: ", x_.shape, y_.shape)
        # distance = np.sqrt(
        #     np.power(x_ - view_box_mouse_x, 2) +
        #     np.power(y_ - view_box_mouse_y, 2)
        # )
        # logger.info(" shape distance:: ", distance.shape)
        # min_distance_arg = np.argmin(distance)
        # min_distance = np.min(distance)
        #
        # logger.info(" Mouse move:: ", self.mouse_x_absolute, self.mouse_y_absolute, " | ", normalized_x, normalized_y, " || ",
        #       view_box_mouse_x, view_box_mouse_y, " ||| ", plot_index, min_distance, min_distance_arg)

        self.mouse_x = view_box_mouse_x
        self.mouse_y = view_box_mouse_y

    #
    # Automated actions
    def reset_axis_limits(self, ax_index=None, direction=None):
        self.hide_info_panels()
        if ax_index is None:
            axes_to_modify = [i for i in range(len(self.view_boxes))]
        else:
            axes_to_modify = (ax_index, )

        for ax_i in axes_to_modify:
            if len(self.x_data_min) >= ax_i - 1:
                if direction is None:
                    logger.info(' zooming home, all directions:',
                          ax_i, self.x_data_max[ax_i], self.x_data_min[ax_i], self.y_data_max[ax_i], self.y_data_min[ax_i])
                    self.view_boxes[ax_i].camera.set_range(
                        (self.x_data_min[ax_i], self.x_data_max[ax_i]),
                        (self.y_data_min[ax_i], self.y_data_max[ax_i]),
                        margin=0.05,
                    )
                else:
                    kwargs = {'view': self.view_boxes[ax_i]}
                    if direction < 0:
                        if direction == -1:
                            func = self.canvas.zoom_in_x
                        elif direction == -2:
                            func = self.canvas.zoom_out_x
                        else:
                            func = self.canvas.zoom_all_out_x
                            kwargs.update({
                                'lims': (self.x_data_min[ax_i], self.x_data_max[ax_i])
                            })
                    else:
                        if abs(direction) == 1:
                            func = self.canvas.zoom_in_y
                        elif abs(direction) == 2:
                            func = self.canvas.zoom_out_y
                        else:
                            func = self.canvas.zoom_all_out_y
                            kwargs.update({
                                'lims': (self.y_data_min[ax_i], self.y_data_max[ax_i])
                            })
                    func(**kwargs)

    def set_axis_limits(self, ax_index, x0, x1, y0, y1, margin=0.005):
        self.hide_info_panels()
        self.view_boxes[ax_index].set_range(
            (x0, x1),
            (y0, y1),
            margin=margin,
        )

    def adapt_canvas_size(self):
        self.hide_info_panels()

        w, h = self.GetSize()
        self.canvas.size = (w, h)

    def on_show(self, event):
        self.canvas.show()
        event.Skip()

    def on_repaint(self, event):
        self.resized = True
        event.Skip()

    def on_idle(self, event):
        # Hack to initialize vispy plot
        if self.initialized < 100:
            self.initialized += 1
            if self.initialized == 100:
                if hasattr(self.main_frame, 'master'):
                    if hasattr(self.main_frame.master, 'post_vispy_init'):
                        self.main_frame.master.post_vispy_init()

        if self.show_tooltip_panel:
            self.update_tooltip_panel()

        if self.show_legend_panel:
            self.update_legend_panel()

        if self.resized:
            self.resized = False
            self.adapt_canvas_size()
            event.Skip()

    def toggle_axis(self):
        self.hide_info_panels()
        ax_elements = self.x_axis + self.y_axis + self.gridlines
        for axis in ax_elements:
            if axis.visible:
                axis.visible = False
            else:
                axis.visible = True
        logger.info(" hiding axes::: ", )

    def toggle_viewbox(self):
        self.hide_info_panels()
        if self.view_boxes[0].visible:
            self.view_boxes[0].visible = False
        else:
            self.view_boxes[0].visible = True

    #
    # Create plot widgets
    def add_line_set(self, n_lines, n_per_line, view_index=None):
        if view_index is not None:
            self.selected_view_index = view_index
            self.line_labels[view_index] = [None for _ in range(n_lines)]

        if self.selected_view_index in self.data_sets:
            # self.data_sets[self.selected_view_index][0] = np.empty(shape=(n_lines, n_per_line, 2), dtype=np.float32)
            # self.data_sets[self.selected_view_index][1] = np.empty(shape=(n_lines, n_per_line, 4), dtype=np.float32)
            for i in range(n_lines):
                self.data_sets[self.selected_view_index][i] = VispyLine(
                    n_size=n_per_line, n_size_init=n_per_line, line_index=i, n_lines=n_lines)
                self.data_sets[self.selected_view_index][i].set_line_size(n_per_line)
        else:
            # self.data_sets[self.selected_view_index] = [
            #     np.empty(shape=(n_lines, n_per_line, 2), dtype=np.float32),  # vertex coordinates
            #     np.empty(shape=(1, 0, 2), dtype=np.float32),  # if a image
            # ]
            self.data_sets[self.selected_view_index] = {
                i: VispyLine(
                    n_size=n_per_line, line_index=i, n_lines=n_lines)
                for i in range(n_lines)
            }
            for i in range(n_lines):
                self.data_sets[self.selected_view_index][i].set_line_size(n_per_line)

        n_tot = n_lines * (n_per_line + 1)
        pos = np.zeros((n_tot, 2), dtype=np.float32)
        pos[:] = np.nan
        color = np.ones((n_tot, 4), dtype=np.float32)
        line = scene.visuals.Line(pos=pos, color=color, method='gl')
        self.lines[self.selected_view_index] = line
        self.view_boxes[self.selected_view_index].add(line)

    def add_image(self, img_shape, view_index=None):
        if view_index is not None:
            self.selected_view_index = view_index

    def add_vertical_line(self, pos=0, view_index=None, color=(1.0, 1.0, 1.0, 1.0)):
        l_ = scene.InfiniteLine(pos, color)
        self.view_boxes[view_index].add(l_)
        self.vertical_lines.append(l_)

    def add_horizontal_line(self, pos=0, view_index=None, color=(1.0, 1.0, 1.0, 1.0)):
        l_ = scene.InfiniteLine(pos, color, vertical=False,)
        self.view_boxes[view_index].add(l_)
        self.horizontal_lines.append(l_)

    #
    # Update plot widgets
    def select_view_index(self, view_index):
        self.selected_view_index = view_index

    def update_line(self, line_index, view_index=None, y_data=None, x_data=None, color=None, label=None, show=True):
        if view_index is not None:
            self.selected_view_index = view_index
        else:
            view_index = self.selected_view_index

        # We have 1 ekstra vertex for splitting the lines visually
        # n_data = self.data_sets[self.selected_view_index][0].shape[1]
        # start_indx = n_data * line_index + line_index
        # end_indx = start_indx + n_data + 1
        line = self.data_sets[view_index][line_index]
        self.pending_line_updates.append(view_index*1000 + line_index)
        line.set_show_mode(show=show, normalize=False)

        # pos = self.lines[view_index].pos
        # color_arr = self.lines[view_index].color

        if label is not None:
            line.set_label(label=label)
            if view_index in self.line_labels.keys():
                self.line_labels[view_index][line_index] = label

        if x_data is not None:
            # self.data_sets[self.selected_view_index][0][line_index, :x_data.size, 0] = x_data[:]
            # pos[start_indx:start_indx+x_data.size, 0] = x_data[:]
            # pos[start_indx+x_data.size: end_indx, 0] = np.nan
            line.set_x_data(x_data)

        if y_data is not None:
            # self.data_sets[self.selected_view_index][0][line_index, :y_data.size, 1] = y_data[:]
            # pos[start_indx:start_indx+y_data.size, 1] = y_data[:]
            # pos[start_indx+y_data.size: end_indx, 0] = np.nan
            line.set_y_data(y_data)

        if color is not None:
            if color == 'auto':
                c = wx.Colour(ColorsCyclic.get_color())
            elif isinstance(color, int):
                c = wx.Colour(ColorsCyclic.get_color_by_index(color))
            else:
                c = wx.Colour(color)

            logger.info("  update_line:: SETTING COLOR", color, isinstance(color, int), isinstance(color, str), c)
            line.set_color(c)
            # logger.info(" c - ", c, type(c))
            # r, g, b = c.Red(), c.Green(), c.Blue()
            # color_arr[start_indx:end_indx, :] = np.array([r, g, b, 255], dtype=np.float32) / 255
            # self.lines[view_index].set_data(pos=pos, color=color_arr)
        # else:
        #     self.lines[view_index].set_data(pos=pos)
        # self.refresh_lines()

    def update_line_split_view(self, line_index, view_index=None, y_data=None, x_data=None, color=None, label=None, split_view=None, show=True):
        if view_index is not None:
            self.selected_view_index = view_index

        line = self.data_sets[self.selected_view_index][line_index]
        self.pending_line_updates.append(self.selected_view_index*1000 + line_index)

        line.set_show_mode(show=show, normalize=True)
        if split_view is not None:
            line.set_split_view_col_and_row(*split_view)

        if label is not None:
            line.set_label(label=label)
            if view_index in self.line_labels.keys():
                self.line_labels[view_index][line_index] = label

        if x_data is not None:
            # logger.info(" new x data?? ", x_data.shape, np.amax(x_data), np.amin(x_data), line_index, view_index, color, label, split_view)
            line.set_x_data(x_data)

        if y_data is not None:
            line.set_y_data(y_data)

        if color is not None:
            if color == 'auto':
                c = wx.Colour(ColorsCyclic.get_color())
            elif isinstance(color, int):
                c = wx.Colour(ColorsCyclic.get_color_by_index(color))
            else:
                c = wx.Colour(color)

            # logger.info("  update_line_split_view:: SETTING COLOR", color, isinstance(color, int), isinstance(color, str), c)
            line.set_color(c)

    def refresh_lines(self, enforce=False):
        if self.get_time_now_ms() - self.time_of_last_refresh > self.minimum_refresh_rate_ms or enforce:
            self.time_of_last_refresh = self.get_time_now_ms()
            views_updated = []
            pos_vals = {}
            color_vals = {}
            for view_line_val in self.pending_line_updates:
                view_index = view_line_val // 1000
                if view_index not in pos_vals:
                    pos_vals[view_index] = self.lines[view_index].pos.copy()
                pos_all = pos_vals[view_index]

                line_index = view_line_val % 1000
                line = self.data_sets[view_index][line_index]

                pos_this_line, start_indx, end_indx = line.get_data()
                pos_all[start_indx: end_indx, :] = pos_this_line[:, :]
                views_updated.append(view_index)

                # y_max, y_min = np.amax(pos_all[start_indx: end_indx, 1]), np.amin(pos_all[start_indx: end_indx, 1])
                # x_max, x_min = np.amax(pos_all[start_indx: end_indx, 0]), np.amin(pos_all[start_indx: end_indx, 0])
                # logger.info(" refreshing lines::: ", line.initialized, line.n_size, line.n_size_init, line.label, view_index)
                # logger.info("    -  x :", pos_all[start_indx: start_indx + line.n_size, 0].mean())
                # logger.info("    -  y :", pos_all[start_indx: start_indx + line.n_size, 1].mean())
                # logger.info("    - ", y_min, y_max, x_min, x_max, "  | ", start_indx, end_indx)

                if line.update_color:
                    # logger.info(" also updating color--- ", view_index, line_index)
                    if view_index not in color_vals:
                        color_vals[view_index] = self.lines[view_index].color.copy()
                    # col_all = color_vals[view_index]
                    # color_of_this_line = line.get_color_data()
                    color_of_this_line = line.get_color_single_point()
                    # logger.info(" colors :: ", color_vals[view_index].shape, color_of_this_line.shape, color_of_this_line)
                    color_vals[view_index][start_indx: end_indx, :] = color_of_this_line[0, :]# color_this_line[: end_indx - start_indx, :]

            self.pending_line_updates = []

            for view_index in list(set(views_updated)):
                # logger.info(" REFRESHING LINES---", view_index, view_index in color_vals)
                pos = pos_vals[view_index]
                non_nans_mask = ~np.isnan(pos[:, 1]) & ~np.isnan(pos[:, 0])

                if view_index in color_vals:
                    # logger.info(" -- color_vals", color_vals[view_index].shape)
                    # logger.info(" -- pos:: ", pos[non_nans_mask, :],)
                    # logger.info(" -- color_vals:: ",color_vals[view_index][non_nans_mask, :])
                    self.lines[view_index].set_data(pos=pos, color=color_vals[view_index])
                else:
                    # logger.info(" -- pos:: ", pos[non_nans_mask, :])
                    self.lines[view_index].set_data(pos=pos)


                # x_masked = pos[non_nans_mask, 0]
                # y_masked = pos[non_nans_mask, 1]
                if np.count_nonzero(non_nans_mask) > 1:
                    self.x_data_min[view_index] = np.amin(pos[non_nans_mask, 0])
                    self.x_data_max[view_index] = np.amax(pos[non_nans_mask, 0])
                    self.y_data_min[view_index] = np.amin(pos[non_nans_mask, 1])
                    self.y_data_max[view_index] = np.amax(pos[non_nans_mask, 1])
                # logger.info(" -- ", np.count_nonzero(non_nans_mask))
                # logger.info("     self.x_data_min", self.x_data_min[view_index])
                # logger.info("     self.x_data_max", self.x_data_max[view_index])
                # logger.info("     self.y_data_min", self.y_data_min[view_index])
                # logger.info("     self.y_data_max", self.y_data_max[view_index])

    def hide_line(self, line_index, view_index=None):
        if view_index is not None:
            self.selected_view_index = view_index

    def update_vertical_line(self, line_index, view_index=None, pos=None, color=None):
        if view_index is not None:
            self.selected_view_index = view_index

    def zoom_axis_home(self):
        i = self.selected_view_index
        vb = self.view_boxes[self.selected_view_index]
        vb.camera.set_range(
            (self.x_data_min[i], self.x_data_max[i]), (self.y_data_min[i], self.y_data_max[i]),
            margin=0.1
        )

    #
    def update_tooltip_panel(self):
        # TODO TODO
        if self.IsShown():
            if self.mouse_moved and not self.mouse_dragging:
                # logger.info(" - ", self.mouse_moved)
                if self.tooltip_timer.has_timed_out():
                    self.mouse_moved = False
                    self.tooltip_timer.reset_timer()
                    self.tooltip_timer.reset_long_timer()
                    # logger.info(" updating widget..")
                    # logger.info(" - ", self.mouse_x, self.mouse_y)
                    # logger.info(" - ", self.mouse_x_absolute, self.mouse_y_absolute)
                    # logger.info(" - ", self.GetSize())
                    # logger.info(" - ", self.tooltip_panel.GetPosition())
                    # logger.info("   - view under mouse: ", self.mouse_over_plot)
                    self.tooltip_panel.SetPosition((self.mouse_x_absolute + 15, self.mouse_y_absolute - 20))
                    self.tooltip_panel.update_widget()
                    self.tooltip_panel.Show()
                    # TODO only show tooltip when mouse is close to an graph
                    # TODO tooltip should show: plot-label, mouse_x_vs_plot_y, local high_peak, local low_peak,


                    # if not self.tooltip_panel.IsShown():
                    #     self.tooltip_panel.Show()
                    #     if self.show_legend_panel:
                    #         for wx_ in self.legend_panels:
                    #             wx_.Show()
                # else:
                #     logger.info(" tooltip is showned but not timeout")
            else:
                if self.tooltip_panel.IsShown():
                    # logger.info(" tooltip is showned but no mouse actions.... ", time.perf_counter_ns() - self.tooltip_timer.long_time_last_event, self.tooltip_timer.timeout_long_limit_ms * 1e6)
                    if self.tooltip_timer.has_time_out_long():
                        self.tooltip_panel.Hide()

    def update_legend_panel(self):
        # TODO move legend panel to opposite side of the mouse
        # TODO write selected line (line closest to mouse) with bold font
        # TODO add stats toggle-button, stats should be -mean, -peak_low, peak_high
        if self.IsShown():
            if self.mouse_moved:
                pass

    def hide_info_panels(self):
        # TODO
        for wx_panel in self.legend_panels:
            wx_panel.Hide()
        self.tooltip_panel.Hide()


class LegendPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logger.info(" parent", self.GetParent())
        logger.info(" -- ", self.GetParent().show_legend_panel)

        # self.SetBackgroundColour(wx.Colour(255, 255, 10, 50))
        # self.SetOwnBackgroundColour(wx.Colour(255, 10, 255, 50))
        self.SetTransparent(0)
        # self.SetWindowStyle(style=wx.TRANSPARENT_WINDOW)
        # self.Layout()
        logger.info(" --> ", self.GetBackgroundColour(), self.GetBackgroundStyle())

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.labels = []
        self.stats = []

        button = wx.Button(self, -1, size=(-1, -1), label='Vispy Knapp')
        gd_button = wxgb.GradientButton(self, -1, size=(-1, -1), label='Vispy Gradient Knapp')
        static_text = wx.StaticText(self, -1, label="Statisk tekst")

        self.main_sizer.Add(button, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        self.main_sizer.AddSpacer(15)
        self.main_sizer.Add(gd_button, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        self.main_sizer.AddSpacer(15)
        self.main_sizer.Add(static_text, 0, wx.ALL | wx.ALIGN_CENTER, 0)

        self.SetSizerAndFit(sizer=self.main_sizer)

    def add_label(self, label):
        pass

    def _label_toggle_callback(self, event):
        pass


class ToolTip(wx.Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetBackgroundColour((255, 255, 255))

        # self.SetTransparent(0)

        self.label_txt = ""
        self.mouse_p_txt = ""
        self.local_stats = ""
        self.line_stats = ""

        self.gd_button = wx.StaticText(self, -1, label="", size=(250, -1))
        self.mouse_point_txt = wx.StaticText(self, -1, label="", size=(-1, -1))
        self.local_stats_txt = wx.StaticText(self, -1, label="", size=(-1, -1))
        self.stats_txt = wx.StaticText(self, -1, label="", size=(-1, -1))

        self.main_sizer.Add(self.gd_button, 1, wx.LEFT | wx.TOP | wx.ALIGN_CENTER, 10)
        self.main_sizer.AddSpacer(15)
        self.main_sizer.Add(self.mouse_point_txt, 1, wx.LEFT | wx.ALIGN_LEFT, 5)
        self.main_sizer.AddSpacer(25)
        self.main_sizer.Add(self.local_stats_txt, 1, wx.LEFT | wx.ALIGN_LEFT, 5)
        self.main_sizer.AddSpacer(15)
        self.main_sizer.Add(self.stats_txt, 1, wx.LEFT | wx.ALIGN_LEFT, 5)

        self.SetSizerAndFit(sizer=self.main_sizer)

    def update_widget(self):
        self.gd_button.SetLabel(self.label_txt)
        self.mouse_point_txt.SetLabel(self.mouse_p_txt)
        self.local_stats_txt.SetLabel(self.local_stats)
        self.stats_txt.SetLabel(self.line_stats)

        # self.Update()
        # self.Layout()

    def update_info(self, info_data: MousePointerInfo):

        if self.IsShown():
            # logger.info(" updating info data:: ", info_data)
            # logger.info(" - ", info_data.label)

            self.label_txt = f"{info_data.label}"
            self.mouse_p_txt = f"x = {info_data.point_x:{info_data.print_notation}} [{info_data.x_unit}]  ,  "
            self.mouse_p_txt += f"y = {info_data.point_y:{info_data.print_notation}} [{info_data.y_unit}]"

            self.local_stats = f"Local max = {info_data.stats_local_max:{info_data.print_notation}}  ,  "
            self.local_stats += f"min = {info_data.stats_local_min:{info_data.print_notation}} [{info_data.y_unit}]  ,  "
            self.local_stats += f"mean = {info_data.stats_local_mean:{info_data.print_notation}} [{info_data.y_unit}]"

            self.line_stats = f"Line max = {info_data.stats_max:{info_data.print_notation}}  ,  "
            self.line_stats += f"min = {info_data.stats_min:{info_data.print_notation}} [{info_data.y_unit}]  ,  "
            self.line_stats += f"mean = {info_data.stats_mean:{info_data.print_notation}} [{info_data.y_unit}]"
