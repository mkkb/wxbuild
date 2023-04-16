# --------------------------------------------------------------------------------- #
# MOTOR CONTROL RPM AND TORQUE CURRENT wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.dcdc_state.DcdcStateDisplay` is another
custom-drawn data info class


Description
===========

:class:`DcdcStateDisplay` is another custom-drawn info class

"""

import wx


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`DcdcStateDisplay`. """


class DcdcStateDisplay(wx.Control):
    """ This is the main class implementation of :class:`DcdcStateDisplay`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="dcdcstatedisplay"):
        """
        Default class constructor.

        :param `parent`: the :class:`DcdcStateDisplay` parent;
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

        self.widget_enable = False
        self.current_value = 0.1  # Must be normalized (0, 1)
        self.current_real_value = 0
        self.current_str_format = '>4.0f'
        self.current_unit = 'mA'
        self.voltage_value = 0.1  # Must be normalized (0, 1)
        self.voltage_real_value = 0
        self.voltage_str_format = '>3.0f'
        self.voltage_unit = 'V'
        #
        self.current_limit_a = 0.0
        self.current_limit_a_color = wx.RED
        self.current_limit_b = 0.7
        self.current_limit_b_color = wx.RED
        self.voltage_limit_a = 0.0
        self.voltage_limit_a_color = wx.RED
        self.voltage_limit_b = 0.9
        self.voltage_limit_b_color = wx.RED

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(65, 27)
        self.SetInitialSize(size)

        self.SetBaseColours()

    def SetBitmapLabel(self, bitmap):
        """
        Sets the bitmap label for the button.

        :param `bitmap`: the bitmap label to set, an instance of :class:`wx.Bitmap`.
        """

        self._bitmap = bitmap
        self.Refresh()

    def SetBaseColours(self):
        self._disable_color_very_light = wx.Colour(200, 200, 200, 255)
        self._disable_color_light = wx.Colour(150, 150, 150, 255)
        self._disable_color = wx.Colour(90, 90, 90, 255)
        self._enable_color_light = wx.Colour(90, 90, 255, 255)
        self._enable_color = wx.Colour(50, 50, 255, 255)
        self._no_color = wx.Colour(0, 0, 0, 0)

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`DcdcStateDisplay`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`DcdcStateDisplay`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        # dc.SetBackground(wx.Brush(wx.Colour(230, 230, 255, 155)))
        dc.Clear()

        font_pixel_size = 7
        font = wx.Font(wx.FontInfo(font_pixel_size).Bold()) # wx.Font(wx.FontInfo(7).Bold().Underline())

        clientRect = self.GetClientRect()
        x0, y0, w_, h_ = clientRect

        paths = []
        brushes = []
        pens = []

        high_color = self._disable_color_very_light
        if self.widget_enable:
            low_color = self._enable_color_light
        else:
            low_color = self._disable_color_light

        if self._mouseAction == HOVER:
            hover_extra = h_ * 0.03
        else:
            hover_extra = 0

        bar_height = h_*0.2 + hover_extra
        bar_length = w_
        bar_2_y_offset = h_ - bar_height

        # Start of bar
        x_1 = x0 + bar_height*0.05 #- hover_extra / 2
        y_1 = y0 + bar_height*0.01 #- hover_extra / 2

        # ----- Creating Current Bar ---------------------------------------------------------------
        bar_width_part1 = self.current_value * bar_length
        bar_width_part2 = bar_length - bar_width_part1

        path1 = gc.CreatePath()
        path1.AddRectangle(x=x_1, y=y_1, w=bar_width_part1, h=bar_height)
        path2 = gc.CreatePath()
        path2.AddRectangle(x=x_1 + bar_width_part1, y=y_1, w=bar_width_part2, h=bar_height)

        # Add text under current bar
        if self.widget_enable:
            txt_str = f"{self.current_real_value:{self.current_str_format}} {self.current_unit}"
            gc.SetFont(font, wx.Colour(0,0,0,255))
            gc.DrawText(str=txt_str,
                        x=x_1, y=y_1 + bar_height + h_*0.04 - hover_extra)

        brushes.append(wx.Brush(low_color))
        brushes.append(wx.Brush(high_color))
        pens.append(wx.Pen(self._no_color, width=1, style=wx.PENSTYLE_SOLID), )
        pens.append(None)
        paths.append(path1)
        paths.append(path2)

        if self.current_limit_a > 0:
            path3 = gc.CreatePath()
            path3.AddRectangle(x=self.current_limit_a*bar_length, y=y_1, w=1, h=bar_height)
            path4 = gc.CreatePath()
            path4.AddRectangle(x=self.current_limit_b*bar_length, y=y_1, w=1, h=bar_height)

            pens.append(None)
            pens.append(None)
            brushes.append(wx.Brush(self.current_limit_a_color))
            brushes.append(wx.Brush(self.current_limit_b_color))
            paths.append(path3)
            paths.append(path4)

        # ----- Creating Voltage Bar ---------------------------------------------------------------
        bar_width_part1 = self.voltage_value * bar_length
        bar_width_part2 = bar_length - bar_width_part1

        path1 = gc.CreatePath()
        path1.AddRectangle(x=x_1, y=y_1 + bar_2_y_offset, w=bar_width_part1, h=bar_height)
        path2 = gc.CreatePath()
        path2.AddRectangle(x=x_1 + bar_width_part1, y=y_1 + bar_2_y_offset, w=bar_width_part2, h=bar_height)

        # Add text over voltage bar
        if self.widget_enable:
            txt_str = f"{self.voltage_real_value:{self.voltage_str_format}} {self.voltage_unit}"
            txt_scale = len(txt_str) * font_pixel_size
            gc.DrawText(str=txt_str,
                        x=x_1 + w_ - txt_scale*0.67,
                        y=y_1 + bar_height + h_ * 0.21, )  # Brush, Angle

        brushes.append(wx.Brush(low_color))
        brushes.append(wx.Brush(high_color))
        pens.append(None)
        pens.append(None)
        paths.append(path1)
        paths.append(path2)

        if self.voltage_limit_a > 0:
            path3 = gc.CreatePath()
            path3.AddRectangle(x=self.voltage_limit_a*bar_length, y=y_1 + bar_2_y_offset, w=1, h=bar_height)
            path4 = gc.CreatePath()
            path4.AddRectangle(x=self.voltage_limit_b*bar_length, y=y_1 + bar_2_y_offset, w=1, h=bar_height)

            pens.append(None)
            pens.append(None)
            brushes.append(wx.Brush(self.voltage_limit_a_color))
            brushes.append(wx.Brush(self.voltage_limit_b_color))
            paths.append(path3)
            paths.append(path4)

        for i in range(len(paths)):
            if pens[i] is not None:
                gc.SetPen(pens[i])
            if brushes[i] is not None:
                gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`DcdcStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`DcdcStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

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

    SetBestSize = SetInitialSize

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

    def SetWidgetEnable(self, enable: bool):
        self.widget_enable = enable
        self.Refresh()

    def SetCurrentValueNormalized(self, value: float):
        self.current_value = min(1.0, max(0.0, value))
        self.Refresh()

    def SetCurrentValue(self, value: float):
        self.current_real_value = value
        self.Refresh()

    def SetVoltageValueNormalized(self, value: float):
        self.voltage_value = min(1.0, max(0.0, value))
        self.Refresh()

    def SetVoltageValue(self, value: float):
        self.voltage_real_value = value
        self.Refresh()

    def SetCurrentSetpoins(self, val_a=None, val_b=None, color_a=None, color_b=None):
        if val_a is not None:
            self.current_limit_a = val_a
        if color_a is not None:
            self.current_limit_a_color = wx.Colour(color_a)
        if val_b is not None:
            self.current_limit_b = val_b
        if color_b is not None:
            self.current_limit_b_color = wx.Colour(color_b)
        self.Refresh()

    def SetVoltageSetpoins(self, val_a=None, val_b=None, color_a=None, color_b=None):
        if val_a is not None:
            self.voltage_limit_a = val_a
        if color_a is not None:
            self.voltage_limit_a_color = wx.Colour(color_a)
        if val_b is not None:
            self.voltage_limit_b = val_b
        if color_b is not None:
            self.voltage_limit_a_color = wx.Colour(color_b)
        self.Refresh()

    #
    def SetForegroundColour(self, colour):
        """
        Sets the :class:`DcdcStateDisplay` foreground (text) colour.

        :param `colour`: a valid :class:`wx.Colour` object.

        :note: Overridden from :class:`wx.Control`.
        """

        wx.Control.SetForegroundColour(self, colour)
        self.Refresh()

    def DoGetBestSize(self):
        """
        Overridden base class virtual. Determines the best size of the
        button based on the label and bezel size.

        :note: Overridden from :class:`wx.Control`.
        """

        label = self.GetLabel()
        print("DoGetBestSize: label=", label)
        if not label:
            return wx.Size(112, 48)

        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont())
        retWidth, retHeight = dc.GetTextExtent(label)

        bmpWidth = bmpHeight = 0
        constant = 15
        if self._bitmap:
            bmpWidth, bmpHeight = self._bitmap.GetWidth()+10, self._bitmap.GetHeight()
            retWidth += bmpWidth
            retHeight = max(bmpHeight, retHeight)
            constant = 15

        return wx.Size(retWidth+constant, retHeight+constant)

    def SetDefault(self):
        """ Sets the default button. """

        tlw = wx.GetTopLevelParent(self)
        if hasattr(tlw, 'SetDefaultItem'):
            tlw.SetDefaultItem(self)
