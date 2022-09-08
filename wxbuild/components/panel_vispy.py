from dataclasses import dataclass
import wx
from vispy import scene
import numpy as np

from wxbuild.components.styles_colors import ColorsCyclic

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

        self.N = 64
        self.data_info = []
        self.data_sets = {  # One set per viewbox
            0 : [
                np.empty(shape=(1, 0, 2), dtype=np.float32),  # vertex coordinates
                np.empty(shape=(1, 0, 4), dtype=np.float32),  # vertex colors
                np.empty(shape=(1, 0, 2), dtype=np.float32),  # if a image
            ],
        }
        self.selected_view_index = 0

        self.play = True
        self.play_color = (1, 0, 0, 1)
        self.pause_color = (1, 0, 0, 1)
        self.show_crosshair = False

        self.resized = False
        self.canvas = VispyCanvas(app='wx', parent=self, keys='interactive', bgcolor='black', size=kwargs['size'])
        grid = self.canvas.central_widget.add_grid(spacing=0)

        self.mouse_over_plot = 0
        self.mouse_x = 0
        self.mouse_y = 0
        #
        self.view_boxes = []
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
        self.canvas.events.key_press.connect(self.key_pressed)
        self.canvas.events.mouse_move.connect(self.mouse_moved)
        self.canvas.events.mouse_press.connect(self.mouse_pressed)

    def post_init(self):
        pass

    def mouse_pressed(self, event):
        pass

    def mouse_moved(self, event):
        self.get_mouse_view_box_coordinates(event)

    def key_pressed(self, event):
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
        mouse_x, mouse_y = event.pos

        view_box = self.view_boxes[plot_index]

        rect_x, rect_y = [getattr(view_box.rect, attrib) for attrib in ['right', 'top']]

        row, col = plot_index // self.plot_rows, plot_index % self.plot_cols
        mouse_x_vb, mouse_y_vb = mouse_x - col * rect_x, mouse_y - row*rect_y

        x_camera_rect_pos, y_camera_rect_pos = view_box.camera.rect.pos
        x_camera_rect_size, y_camera_rect_size = view_box.camera.rect.size

        normalized_x, normalized_y = mouse_x_vb / rect_x, 1 - mouse_y_vb / rect_y
        view_box_mouse_x = normalized_x * x_camera_rect_size + x_camera_rect_pos
        view_box_mouse_y = normalized_y * y_camera_rect_size + y_camera_rect_pos

        self.mouse_x = view_box_mouse_x
        self.mouse_y = view_box_mouse_y

    #
    # Automated actions
    def reset_axis_limits(self, ax_index=None, direction=None):
        if ax_index is None:
            axes_to_modify = [i for i in range(len(self.view_boxes))]
        else:
            axes_to_modify = (ax_index, )

        for ax_i in axes_to_modify:
            if len(self.x_data_min) >= ax_i - 1:
                if direction is None:
                    print(' zooming home, all directions:', ax_i, self.x_data_max, self.x_data_min, self.y_data_max, self.y_data_min)
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
        self.view_boxes[ax_index].set_range(
            (x0, x1),
            (y0, y1),
            margin=margin,
        )

    def adapt_canvas_size(self):
        w, h = self.GetSize()
        self.canvas.size = (w, h)

    def on_show(self, event):
        self.canvas.show()
        event.Skip()

    def on_repaint(self, event):
        self.resized = True
        event.Skip()

    def on_idle(self, event):
        if self.resized:
            self.resized = False
            self.adapt_canvas_size()
            event.Skip()

    def toggle_axis(self):
        ax_elements = self.x_axis + self.y_axis + self.gridlines
        for axis in ax_elements:
            if axis.visible:
                axis.visible = False
            else:
                axis.visible = True
        print(" hiding axes::: ", )

    def toggle_viewbox(self):
        if self.view_boxes[0].visible:
            self.view_boxes[0].visible = False
        else:
            self.view_boxes[0].visible = True

    #
    # Create plot widgets
    def add_line_set(self, n_lines, n_per_line, view_index=None):
        if view_index is not None:
            self.selected_view_index = view_index

        if self.selected_view_index in self.data_sets:
            self.data_sets[self.selected_view_index][0] = np.empty(shape=(n_lines, n_per_line, 2), dtype=np.float32)
            self.data_sets[self.selected_view_index][1] = np.empty(shape=(n_lines, n_per_line, 4), dtype=np.float32)
        else:
            self.data_sets[self.selected_view_index] = [
                np.empty(shape=(n_lines, n_per_line, 2), dtype=np.float32),  # vertex coordinates
                np.empty(shape=(1, 0, 2), dtype=np.float32),  # if a image
            ]

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
        l = scene.InfiniteLine(pos, color)
        self.view_boxes[view_index].add(l)
        self.vertical_lines.append(l)

    #
    # Update plot widgets
    def select_view_index(self, view_index):
        self.selected_view_index = view_index

    def update_line(self, line_index, view_index=None, y_data=None, x_data=None, color=None):
        if view_index is not None:
            self.selected_view_index = view_index

        # We have 1 ekstra vertex for splitting the lines visually
        n_data = self.data_sets[self.selected_view_index][0].shape[1]
        start_indx = n_data * line_index + line_index
        end_indx = start_indx + n_data + 1

        pos = self.lines[view_index].pos
        color_arr = self.lines[view_index].color

        if x_data is not None:
            self.data_sets[self.selected_view_index][0][line_index, :x_data.size, 0] = x_data[:]
            pos[start_indx:start_indx+x_data.size, 0] = x_data[:]
            pos[start_indx+x_data.size: end_indx, 0] = np.nan

        if y_data is not None:
            self.data_sets[self.selected_view_index][0][line_index, :y_data.size, 1] = y_data[:]
            pos[start_indx:start_indx+y_data.size, 1] = y_data[:]
            pos[start_indx+y_data.size: end_indx, 0] = np.nan

        if color is not None:
            c = wx.Colour(color)
            r, g, b = c.Red(), c.Green(), c.Blue()

            color_arr[start_indx:end_indx, :] = np.array([r, g, b, 255], dtype=np.float32) / 255
            self.lines[view_index].set_data(pos=pos, color=color_arr)
        else:
            self.lines[view_index].set_data(pos=pos)

        non_nans_mask = ~np.isnan(pos[:, 1]) & ~np.isnan(pos[:, 0])

        self.x_data_min[self.selected_view_index] = np.amin(pos[non_nans_mask, 0])
        self.x_data_max[self.selected_view_index] = np.amax(pos[non_nans_mask, 0])
        self.y_data_min[self.selected_view_index] = np.amin(pos[non_nans_mask, 1])
        self.y_data_max[self.selected_view_index] = np.amax(pos[non_nans_mask, 1])

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