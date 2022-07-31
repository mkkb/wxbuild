from dataclasses import dataclass
import wx
from vispy import scene
import numpy as np


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_flags: int = wx.EXPAND | wx.ALL
    sizer_proportion: float = 1
    sizer_border: int = 0
    sizer_direction: str = 'horizontal'
    shape: tuple = (1, 1)
    size: tuple = (10, 10)


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

    def zoom_in_x(self, view):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = l + w / 2
        new_w = w / 2
        y_lim = (b, t)
        x_lim = (center - new_w, center + new_w)
        view.camera.set_range(x_lim, y_lim, margin=0.0)

    def zoom_out_x(self, view):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = l + w / 2
        new_w = w * 2
        y_lim = (b, t)
        x_lim = (center - new_w, center + new_w)
        view.camera.set_range(x_lim, y_lim, margin=0.0)

    def zoom_in_y(self, view):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = b + h / 2
        new_h = h / 2
        y_lim = (center - new_h, center + new_h)
        x_lim = (b, t)
        view.camera.set_range(x_lim, y_lim, margin=0.0)

    def zoom_out_y(self, view):
        w, h, l, r, b, t = self.get_view_rect(view=view)
        center = b + h / 2
        new_h = h * 2
        y_lim = (center - new_h, center + new_h)
        x_lim = (b, t)
        view.camera.set_range(x_lim, y_lim, margin=0.0)

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
        self.main_frame = main_frame
        self.parent = parent
        if 'shape' in kwargs:
            self.plot_cols, self.plot_rows = kwargs.pop('shape')
        else:
            self.plot_cols, self.plot_rows = 1, 1

        wx.Panel.__init__(self, parent, **kwargs)

        self.N = 64
        self.data_info = []
        self.data_line_buffer = np.empty(shape=(1, 0, 2), dtype=np.float32)
        self.data_line_colors = np.empty(shape=(1, 0, 4), dtype=np.float32)
        self.data_mesh_buffer = np.empty(shape=(1, 0, 2), dtype=np.float32)

        self.play = True
        self.play_color = (1, 0, 0, 1)
        self.pause_color = (1, 0, 0, 1)
        self.show_crosshair = False

        self.resized = False
        self.canvas = VispyCanvas(app='wx', parent=self, keys='interactive', bgcolor='black', size=kwargs['size'])
        grid = self.canvas.central_widget.add_grid(spacing=0)

        self.selected_plot = 0
        self.view_boxes = []
        self.lines = []
        self.line_crosshairs = []
        self.ax_lines = []
        self.x_data_min = []
        self.x_data_max = []
        self.y_data_min = []
        self.y_data_max = []
        # self.plot_names = [self.data_info[i][0]]

        for row in range(self.plot_rows):
            for col in range(self.plot_cols):
                view_box = grid.add_view(row=row, col=col, camera='panzoom', border_color='w')

                x_axis = scene.AxisWidget(orientation='top')
                x_axis.stretch = (1, 0.1)
                grid.add_widget(x_axis, row=row, col=col)
                x_axis.link_view(view_box)

                y_axis = scene.AxisWidget(orientation='right')
                y_axis.stretch = (0.1, 1)
                grid.add_widget(y_axis, row=row, col=col)
                y_axis.link_view(view_box)

                scene.visuals.GridLines(color='w', parent=view_box.scene)
                self.view_boxes.append(view_box)

        self.adapt_canvas_size()
        self.canvas.show()
        self.Bind(wx.EVT_SIZE, self.on_repaint)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.canvas.events.key_press.connect(self.key_pressed)
        self.canvas.events.mouse_move.connect(self.mouse_moved)
        self.canvas.events.mouse_press.connect(self.mouse_pressed)

    def mouse_pressed(self, event):
        pass

    def mouse_moved(self, event):
        self.get_plot_index_from_mouse_coordinates(*event.pos)

    def key_pressed(self, event):
        if hasattr(event.key, 'name'):
            key_char = event.key.name
            if key_char in 'ASHZXCQWE':
                if key_char == 'H':
                    self.reset_axis_limits(ax_index=self.selected_plot)
                elif key_char == 'Z':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)
                elif key_char == 'X':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)
                elif key_char == 'C':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)
                elif key_char == 'Q':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)
                elif key_char == 'W':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)
                elif key_char == 'E':
                    self.reset_axis_limits(ax_index=self.selected_plot, direction=-1)

    #
    def get_plot_index_from_mouse_coordinates(self, mouse_x, mouse_y):
        for i, view_box in enumerate(self.view_boxes):
            x0, x1 = view_box.pos[0], view_box.pos[0] + view_box.width
            y0, y1 = view_box.pos[1], view_box.pos[1] + view_box.height
            if mouse_x >= x0:
                if mouse_x <= x1:
                    if mouse_y >= y0:
                        if mouse_y <= y1:
                            self.selected_plot = i
                            return
        self.selected_plot = -1

    def get_mouse_view_box_coordinates(self, plot_index, mouse_x, mouse_y):
        view_box = self.view_boxes[plot_index]

        rect_x, rect_y = [getattr(view_box.rect, attrib) for attrib in ['right', 'top']]

        row, col = plot_index // self.plot_rows, plot_index % self.plot_cols
        mouse_x_vb, mouse_y_vb = mouse_x - col * rect_x, mouse_y - row*rect_y

        x_camera_rect_pos, y_camera_rect_pos = view_box.camera.rect.pos
        x_camera_rect_size, y_camera_rect_size = view_box.camera.rect.size

        normalized_x, normalized_y = mouse_x_vb / rect_x, 1 - mouse_y_vb / rect_y
        view_box_mouse_x = normalized_x * x_camera_rect_size + x_camera_rect_pos
        view_box_mouse_y = normalized_y * y_camera_rect_size + y_camera_rect_pos

        return view_box_mouse_x, view_box_mouse_y

    #
    def reset_axis_limits(self, ax_index=None, direction=None):
        if ax_index is None:
            axes_to_modify = [i for i in range(len(self.view_boxes))]
        else:
            axes_to_modify = (ax_index, )

        for ax_i in axes_to_modify:
            if len(self.x_data_min >= ax_i - 1):
                if direction is None:
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
