# --------------------------------------------------------------------------------- #
# CUSTOM CONTROL STATE DISPLAY wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.custom_state_display.CustomControlStateDisplay` is another
custom-drawn data info class


Description
===========

:class:`CustomControlStateDisplay` is another custom-drawn info class

"""

import wx
import numpy as np


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`CustomControlStateDisplay`. """
CLICK = 2
""" Flag used to indicate that the :class:`MotorControlAlarmState` is on a pressed state. """


class CustomControlStateDisplayEvent(wx.PyCommandEvent):
    """ Event sent from :class:`CustomControlStateDisplay` when the button is activated. """

    def __init__(self, eventType, eventId):
        """
        Default class constructor.

        :param `eventType`: the event type;
        :param `eventId`: the event identifier.
        """

        wx.PyCommandEvent.__init__(self, eventType, eventId)
        self.isDown = False
        self.theButton = None


    def SetButtonObj(self, btn):
        """
        Sets the event object for the event.

        :param `btn`: the button object, an instance of :class:`CustomControlStateDisplay`.
        """

        self.theButton = btn


    def GetButtonObj(self):
        """ Returns the object associated with this event. """

        return self.theButton


class CustomControlStateDisplay(wx.Control):
    """ This is the main class implementation of :class:`CustomControlStateDisplay`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="customcontrolstatedisplay"):
        """
        Default class constructor.

        :param `parent`: the :class:`CustomControlStateDisplay` parent;
        :param `id`: window identifier. A value of -1 indicates a default value;
        :param `bitmap`: the button bitmap (if any);
        :param `pos`: the control position. A value of (-1, -1) indicates a default position,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `size`: the control size. A value of (-1, -1) indicates a default size,
         chosen by either the windowing system or wxPython, depending on platform;
        :param `style`: the button style (unused);
        :param `align`: text/bitmap alignment. wx.CENTER or wx.LEFT;
        :param `validator`: the validator associated to the button;
        :param `name`: the button name.
        """

        wx.Control.__init__(self, parent, id, pos, size, style, validator, name)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

        self.widget_enable = False
        self._color_disable_dark = wx.Colour(90, 90, 90, 255)
        self._color_disable_light = wx.Colour(200, 200, 200, 255)
        self._color_disable_lightest = wx.Colour(245, 245, 245, 255)
        self._color_enable_dark = wx.Colour(50, 50, 255, 255)
        self._color_enable_light = wx.Colour(90, 90, 255, 255)
        self._setpoint_color = wx.Colour('#0028a6')
        self._disable_text_color = wx.Colour(150, 150, 150, 255)
        self._no_color = wx.Colour(0, 0, 0, 0)
        #
        self.bar_values = []
        self.bar_positions_x = []
        self.bar_positions_y = []
        self.bar_sizes_w = []
        self.bar_sizes_h = []
        self.bar_alignments = []
        self.bar_setpoints = []
        #
        self.text_positions_x = []
        self.text_positions_y = []
        self.text_labels = []
        #
        self.graph_positions_x = []
        self.graph_positions_y = []
        self.graph_sizes_w = []
        self.graph_sizes_h = []
        self._graph_data_size = 256
        self._graph_zoom_levels = 4
        self._graph_current_zoom = 1
        self.graph_data = [np.zeros(self._graph_data_size, dtype=np.float32), ]

        self._mouseAction = None
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(80, 27)
        self.SetInitialSize(size)

    def edit_text_label(self, text: str, index: int) -> None:
        if index >= len(self.text_labels):
            self.text_labels.append(text)
        else:
            self.text_labels[index] = text
        self.Refresh()

    def edit_text_attributes(self, index: int, pos_x=0, pos_y=0, ) -> None:
        if index >= len(self.text_positions_x):
            self.text_positions_x.append(pos_x)
            self.text_positions_y.append(pos_y)
        else:
            self.text_positions_x[index] = pos_x
            self.text_positions_y[index] = pos_y

    def edit_bar_attributes(self, index: int, pos_x=0, pos_y=0, size_w=-1, size_h=-1, alignment=-1, setpoints=()):
        assert alignment in (-1, 0, 1)

        if index >= len(self.bar_values):
            self.bar_values.append(0)
            self.bar_positions_x.append(pos_x)
            self.bar_positions_y.append(pos_y)
            self.bar_sizes_w.append(size_w)
            self.bar_sizes_h.append(size_h)
            self.bar_alignments.append(alignment)
            self.bar_setpoints.append(setpoints)
        else:
            self.bar_positions_x[index] = pos_x
            self.bar_positions_y[index] = pos_y
            self.bar_positions_y[index] = size_w
            self.bar_positions_y[index] = size_h
            self.bar_positions_y[index] = alignment
            self.bar_positions_y[index] = setpoints

    def edit_bar_value(self, index: int, bar_value: int):
        if index >= len(self.bar_values):
            self.bar_values.append(bar_value)
        else:
            self.bar_values[index] = bar_value
        self.Refresh()

    def edit_graph_attributes(self, index: int, pos_x=0, pos_y=0, size_w=-1, size_h=-1):
        if index >= len(self.graph_positions_x):
            self.graph_positions_x.append(pos_x)
            self.graph_positions_y.append(pos_y)
            self.graph_sizes_w.append(size_w)
            self.graph_sizes_h.append(size_h)
            self.graph_data.append(np.zeros(self._graph_data_size, dtype=np.float32))
        else:
            self.graph_positions_x[index] = pos_x
            self.graph_sizes_w[index] = size_w
            self.graph_sizes_h[index] = size_h

    def edit_graph_data(self, index: int, data: np.ndarray):
        assert data.dtype == np.float32
        assert data.size <= self._graph_data_size

        if index >= len(self.graph_data):
            self.graph_data.append(np.zeros(self._graph_data_size, dtype=np.uint16))
            self.graph_data[-1][:data.size] = data[:]
            self.graph_data[-1] = np.roll(self.graph_data[-1], -data.size)
        else:
            self.graph_data[index][:data.size] = data[:]
            self.graph_data[index] = np.roll(self.graph_data[index], -data.size)
        self.Refresh()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`CustomControlStateDisplay`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`CustomControlStateDisplay`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        clientRect = self.GetClientRect()
        x0, y0, w_, h_ = clientRect

        cc_v = 220
        if self._mouseAction == HOVER:
            #
            hover_extra = 0  # h_w * 0.05
            canvas_color = wx.Colour(cc_v, cc_v, cc_v, 255)
        else:
            #
            canvas_color = self.GetParent().GetBackgroundColour()
            hover_extra = 0

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(canvas_color))
        dc.Clear()

        font_pixel_size = 6
        font = wx.Font(wx.FontInfo(font_pixel_size).Bold()) # wx.Font(wx.FontInfo(7).Bold().Underline())

        if self.widget_enable:
            background_color = self._color_disable_light
            foreground_color = self._color_enable_light
            setpoint_color = self._setpoint_color
            txt_color = wx.Colour(0, 0, 0, 255)
            if self._mouseAction == HOVER:
                background_color = self._color_disable_lightest
        else:
            background_color = self._color_disable_lightest
            foreground_color = self._color_disable_dark
            setpoint_color = self._color_disable_dark
            txt_color = self._disable_text_color

        # Draw all text
        gc.SetFont(font, txt_color)
        for i, txt_lbl in enumerate(self.text_labels):
            x = self.text_positions_x[i] * w_
            y = self.text_positions_y[i] * h_
            gc.DrawText(str=txt_lbl, x=x, y=y)
            # w,h = dc.GetTextExtent("test string")

        paths = []
        brushes = []
        pens = []

        # Draw all bars
        for i, x_bar in enumerate(self.bar_values):
            x = self.bar_positions_x[i] * w_
            y = self.bar_positions_y[i] * h_
            w = self.bar_sizes_w[i]
            h = self.bar_sizes_h[i]

            # print(" ... ", self.bar_values)

            alignment = self.bar_alignments[i]

            bar_w_background = w * w_ + hover_extra
            bar_h = h * h_ + hover_extra
            if alignment == 0:
                bar_w_foreground = abs(x_bar - 0.5) * bar_w_background
                if x_bar < 0.5:
                    # x_norm = abs(x_bar - 0.5)
                    x_foreground = x_bar*bar_w_background + x  # x + bar_w_foreground
                else:
                    # x_norm = 0.5
                    x_foreground = x + bar_w_background*0.5
            else:
                bar_w_foreground = x_bar * bar_w_background
                x_foreground = x
            # print(f'x_bar: i={i} || bar_value={x_bar:.2f} | x={x}, y={y}, w={w}, h={h}  |'
            #       f'  x={x_norm:.2f}, w={abs(x_bar - 0.5):.2f}')

            path_background = gc.CreatePath()
            path_background.AddRectangle(x=x, y=y, w=bar_w_background, h=bar_h)

            path_foreground = gc.CreatePath()
            path_foreground.AddRectangle(x=x_foreground, y=y, w=bar_w_foreground, h=bar_h)

            brushes.append(wx.Brush(background_color))
            pens.append(wx.Pen(self._no_color, width=1, style=wx.PENSTYLE_SOLID), )
            paths.append(path_background)
            #
            brushes.append(wx.Brush(foreground_color))
            pens.append(None)
            paths.append(path_foreground)


            for sp in self.bar_setpoints[i]:
                # print(f"  -->>  sp={sp}")
                path_sp = gc.CreatePath()
                path_sp.AddRectangle(x=sp * bar_w_background + x, y=y, w=bar_w_background*0.01, h=bar_h)
                brushes.append(wx.Brush(setpoint_color))
                pens.append(None)
                paths.append(path_sp)

        # Draw all graphs
        n = int(self._graph_data_size / (2 ** self._graph_current_zoom))
        for i, x in enumerate(self.graph_positions_x):
            x = self.graph_positions_x[i] * w_
            y = self.graph_positions_y[i] * h_
            w = self.graph_sizes_w[i] * w_
            h = self.graph_sizes_h[i] * h_

            x_data = self.graph_data[i][-n:]
            dx = w / x_data.size

            path_background = gc.CreatePath()
            path_background.AddRectangle(x=x, y=y, w=w, h=h)

            brushes.append(wx.Brush(background_color))
            pens.append(wx.Pen(self._no_color, width=1, style=wx.PENSTYLE_SOLID), )
            paths.append(path_background)

            path_graph_line = gc.CreatePath()
            path_graph_line.MoveToPoint(x, h - x_data[0]*h)
            for j, x_val in enumerate(x_data[1:]):
                path_graph_line.AddLineToPoint(x + j*dx, h - x_data[j]*h)

            paths.append(path_graph_line)
            brushes.append(wx.Brush(self._no_color))  # _disable_color_very_light
            pens.append(wx.Pen(foreground_color))

        for i in range(len(paths)):
            if pens[i] is not None:
                gc.SetPen(pens[i])
            if brushes[i] is not None:
                gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

    def SetWidgetEnable(self, enable: bool):
        self.widget_enable = enable
        self.Refresh()

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`CustomControlStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`CustomControlStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        self._mouseAction = None
        self.Refresh()
        event.Skip()

    def OnLeftDown(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN`` event for :class:`MotorControlAlarmStateEvent`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = CLICK
        self.CaptureMouse()
        self.Refresh()
        event.Skip()

    def OnLeftUp(self, event):
        """
        Handles the ``wx.EVT_LEFT_UP`` event for :class:`MotorControlAlarmStateEvent`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled() or not self.HasCapture():
            return

        pos = event.GetPosition()
        rect = self.GetClientRect()

        self._graph_current_zoom = (self._graph_current_zoom + 1) % self._graph_zoom_levels

        if self.HasCapture():
            self.ReleaseMouse()

        if rect.Contains(pos):
            self._mouseAction = HOVER
            self.Notify()
        else:
            self._mouseAction = None

        self.Refresh()
        event.Skip()

    def GetPath(self, gc, rc, r):
        """
        Returns a rounded :class:`GraphicsPath` rectangle.

        :param `gc`: an instance of :class:`GraphicsContext`;
        :param `rc`: a client rectangle;
        :param `r`: the radious of the rounded part of the rectangle.
        """

        x, y, w, h = rc
        path = gc.CreatePath()
        path.AddRoundedRectangle(x, y, w, h, r)
        path.CloseSubpath()
        return path

    def SetInitialSize(self, size=None):
        """
        Given the current font and bezel width settings, calculate
        and set a good size.

        :param `size`: an instance of :class:`wx.Size`.
        """

        if size is None:
            size = wx.DefaultSize
        wx.Control.SetInitialSize(self, size)
        # print('SetInitialSize -> ', self.GetSize())

    def AcceptsFocus(self):
        """
        Can this window be given focus by mouse click?

        :note: Overridden from :class:`wx.Control`.
        """

        return self.IsShown() and self.IsEnabled()

    def GetDefaultAttributes(self):
        """
        Overridden base class virtual. By default we should use
        the same font/colour attributes as the native :class:`Button`.
        """

        return wx.Button.GetClassDefaultAttributes()

    def ShouldInheritColours(self):
        """
        Overridden base class virtual. Buttons usually don't inherit
        the parent's colours.

        :note: Overridden from :class:`wx.Control`.
        """

        return False

    def Enable(self, enable=True):
        """
        Enables/disables the button.

        :param `enable`: ``True`` to enable the button, ``False`` to disable it.

        :note: Overridden from :class:`wx.Control`.
        """

        wx.Control.Enable(self, enable)
        self.Refresh()

    def SetForegroundColour(self, colour):
        """
        Sets the :class:`CustomControlStateDisplay` foreground (text) colour.

        :param `colour`: a valid :class:`wx.Colour` object.

        :note: Overridden from :class:`wx.Control`.
        """

        wx.Control.SetForegroundColour(self, colour)
        self.Refresh()

    def SetDefault(self):
        """ Sets the default button. """

        tlw = wx.GetTopLevelParent(self)
        if hasattr(tlw, 'SetDefaultItem'):
            tlw.SetDefaultItem(self)

    def Notify(self):
        """ Actually sends a ``wx.EVT_BUTTON`` event to the listener (if any). """

        evt = CustomControlStateDisplayEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)
