# --------------------------------------------------------------------------------- #
# MOTOR CONTROL RPM AND TORQUE CURRENT wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.motorcontrol_rpmcurrent.MotorControlRpmCurrent` is another
custom-drawn data info class


Description
===========

:class:`MotorControlRpmCurrent` is another custom-drawn info class

"""

import wx


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`MotorControlDriveState`. """


class MotorControlRpmCurrent(wx.Control):
    """ This is the main class implementation of :class:`MotorControlRpmCurrent`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="motorcontrolrpmcurrent"):
        """
        Default class constructor.

        :param `parent`: the :class:`MotorControlRpmCurrent` parent;
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

        self.motor_enabled = False
        self.rpm_value = 0.5
        self.rpm_setpoint_a = 0.3
        self.rpm_setpoint_b = 0.8
        self.torque_value = 0.2
        self.torque_setpoint_a = 0.3
        self.torque_setpoint_b = 0.6
        self.torque_setpoint_c = 0.8
        self.rpm_startup_color = wx.Colour('#006607')
        self.rpm_normal_color = wx.Colour('#57ff26')
        self.rpm_alarm_color = wx.Colour('#ff544a')
        self.rpm_setpoint_color = wx.Colour('#006907')
        self.torque_alarm_selected = False  # False => low alarm | True => High alarm
        self.torque_startup_color = wx.Colour('#ffb830')
        self.torque_normal_color = wx.Colour('#57ff26')
        self.torque_alarm_color = wx.Colour('#ff544a')
        self.torque_setpoint_color = wx.Colour('#006907')

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(85, 27)
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
        self._disable_color_light = wx.Colour(90, 90, 90, 255)
        self._enable_color_light = wx.Colour(255, 90, 90, 255)
        self._enable_color = wx.Colour(255, 50, 50, 255)
        self._disable_color = wx.Colour(200, 200, 200, 255)
        self._no_color = wx.Colour(0, 0, 0, 0)

    def LightColour(self, colour, percent):
        """
        Return light contrast of `colour`. The colour returned is from the scale of
        `colour` ==> white.

        :param `colour`: the input colour to be brightened;
        :param `percent`: determines how light the colour will be. `percent` = 100
         returns white, `percent` = 0 returns `colour`.
        """

        end_colour = wx.WHITE
        rd = end_colour.Red() - colour.Red()
        gd = end_colour.Green() - colour.Green()
        bd = end_colour.Blue() - colour.Blue()
        high = 100

        # We take the percent way of the colour from colour -. white
        i = percent
        r = colour.Red() + ((i*rd*100)/high)/100
        g = colour.Green() + ((i*gd*100)/high)/100
        b = colour.Blue() + ((i*bd*100)/high)/100
        a = colour.Alpha()

        return wx.Colour(int(r), int(g), int(b), int(a))

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`MotorControlRpmCurrent`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`MotorControlRpmCurrent`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        # dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.SetBackground(wx.Brush(wx.Colour(230, 230, 255, 255)))
        dc.Clear()

        clientRect = self.GetClientRect()
        x0, y0, w_, h_ = clientRect

        paths = []
        brushes = []
        pens = []

        if self.motor_enabled:
            if self.rpm_value > self.rpm_setpoint_a:
                rpm_low_color = self.rpm_normal_color
            else:
                rpm_low_color = self.rpm_startup_color
            rpm_high_color = self._disable_color

            if self.torque_value > self.torque_setpoint_a:
                torque_low_color = self.torque_normal_color
            else:
                torque_low_color = self.torque_startup_color
            torque_high_color = self._disable_color
            rpm_setpoint_color = self.rpm_setpoint_color
            torque_setpoint_color = self.torque_setpoint_color
        else:
            rpm_low_color = self._disable_color_light
            rpm_high_color = self._disable_color
            torque_low_color = self._disable_color_light
            torque_high_color = self._disable_color
            rpm_setpoint_color = self._disable_color_light
            torque_setpoint_color = self._disable_color_light

        if self.torque_alarm_selected:
            torque_setpoint_color_b = torque_setpoint_color
            torque_setpoint_color_c = self._disable_color_light
        else:
            torque_setpoint_color_b = self._disable_color_light
            torque_setpoint_color_c = torque_setpoint_color

        if self._mouseAction == HOVER:
            hover_extra = (clientRect[3] * 0.03) / 2
            # enable_color = self._enable_color_light
            # disable_color = self._disable_color_light
        else:
            hover_extra = 0
            # enable_color = self._enable_color
            # disable_color = self._disable_color

        r = h_ * 0.2

        x_1 = x0 + r*0.6 + 3 - hover_extra
        y_1 = y0 + r + 1 - hover_extra
        x_2 = x_1 + r*0.3
        y_2 = y_1 - r*0.5

        y_offset = y_1 * 2.
        meter_width = w_*0.9

        # ----- Creating RPM bar ---------------------------------------------------------------
        rpm_setpoint_ = meter_width * (1 - self.rpm_setpoint_a) * self.rpm_setpoint_b
        x_rpm_setpoint = rpm_setpoint_ + x_2

        path1 = gc.CreatePath()
        path1.AddCircle(x=x_1, y=y_1, r=r)

        if self.rpm_value > self.rpm_setpoint_a:
            # l = (1 - self.rpm_setpoint_a)
            l_0 = (self.rpm_value - self.rpm_setpoint_a)/(1 - self.rpm_setpoint_a) * meter_width
            l_1 = (1 - self.rpm_setpoint_a) / (1 - self.rpm_setpoint_a) * meter_width

            path2 = gc.CreatePath()
            path2.AddRectangle(x=x_2, y=y_2, w=l_0, h=r * 1.1, )  # radius=r*0.8)

            path3 = gc.CreatePath()
            path3.AddRectangle(x=x_2 + l_0, y=y_2, w=l_1, h=r * 1.1, )

            #
            paths.append(path2)
            paths.append(path1)
            paths.append(path3)

            brushes.append(wx.Brush(rpm_low_color))
            brushes.append(None)
            brushes.append(wx.Brush(rpm_high_color))

            pens.append(wx.Pen(self._no_color, width=3, style=wx.PENSTYLE_SOLID), )
            pens.append(None)
            pens.append(None)

        else:
            path2 = gc.CreatePath()
            path2.AddRectangle(x=x_2, y=y_2, w=meter_width, h=r * 1.1)

            #
            paths.append(path2)
            paths.append(path1)

            brushes.append(wx.Brush(rpm_high_color))
            brushes.append(wx.Brush(rpm_low_color))

            pens.append(wx.Pen(self._no_color, width=3, style=wx.PENSTYLE_SOLID), )
            pens.append(None)

        path4 = gc.CreatePath()
        path4.AddRectangle(x=x_rpm_setpoint, y=y_1 - r * 1.1, w=r * 0.1, h=r * 2.0)

        paths.append(path4)
        brushes.append(wx.Brush(self._no_color))
        pens.append(wx.Pen(rpm_setpoint_color, width=1, style=wx.PENSTYLE_SOLID), )

        # path1.AddRoundedRectangle(x=xB_1, y=yB_1, w=r * 1.5, h=r, radius=r)

        # ----- Creating Torque bar ---------------------------------------------------------------
        torque_setpoint_ = meter_width * (1 - self.torque_setpoint_a) * self.torque_setpoint_b
        x_torque_setpoint_b = torque_setpoint_ + x_2
        torque_setpoint_ = meter_width * (1 - self.torque_setpoint_a) * self.torque_setpoint_c
        x_torque_setpoint_c = torque_setpoint_ + x_2

        path1 = gc.CreatePath()
        path1.AddCircle(x=x_1, y=y_1+y_offset, r=r)

        if self.torque_value > self.torque_setpoint_a:
            l_0 = (self.torque_value - self.torque_setpoint_a) / (1 - self.torque_setpoint_a) * meter_width
            l_1 = (1 - self.torque_setpoint_a) / (1 - self.torque_setpoint_a) * meter_width

            path2 = gc.CreatePath()
            path2.AddRectangle(x=x_2, y=y_2+y_offset, w=l_0, h=r * 1.1, )  # radius=r*0.8)

            path3 = gc.CreatePath()
            path3.AddRectangle(x=x_2 + l_0, y=y_2+y_offset, w=l_1, h=r * 1.1, )

            #
            paths.append(path2)
            paths.append(path1)
            paths.append(path3)

            brushes.append(wx.Brush(torque_low_color))
            brushes.append(None)
            brushes.append(wx.Brush(torque_high_color))

            pens.append(wx.Pen(self._no_color, width=3, style=wx.PENSTYLE_SOLID), )
            pens.append(None)
            pens.append(None)

        else:
            path2 = gc.CreatePath()
            path2.AddRectangle(x=x_2, y=y_2+y_offset, w=meter_width, h=r * 1.1)

            #
            paths.append(path2)
            paths.append(path1)

            brushes.append(wx.Brush(torque_high_color))
            brushes.append(wx.Brush(torque_low_color))

            pens.append(wx.Pen(self._no_color, width=3, style=wx.PENSTYLE_SOLID), )
            pens.append(None)

        path4 = gc.CreatePath()
        path4.AddRectangle(x=x_torque_setpoint_b, y=y_1 - r * 1.1 +y_offset, w=r * 0.1, h=r * 2.0)
        path5 = gc.CreatePath()
        path5.AddRectangle(x=x_torque_setpoint_c, y=y_1 - r * 1.1 + y_offset, w=r * 0.1, h=r * 2.0)

        paths.append(path4)
        paths.append(path5)
        brushes.append(wx.Brush(self._no_color))
        brushes.append(wx.Brush(self._no_color))
        pens.append(wx.Pen(torque_setpoint_color_b, width=1, style=wx.PENSTYLE_SOLID), )
        pens.append(wx.Pen(torque_setpoint_color_c, width=1, style=wx.PENSTYLE_SOLID), )

        for i in range(len(paths)):
            if pens[i] is not None:
                gc.SetPen(pens[i])
            if brushes[i] is not None:
                gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`MotorControlRpmCurrent`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`MotorControlRpmCurrent`.

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
        print('SetInitialSize -> ', self.GetSize())

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

    def SetMotorEnable(self, enable: bool):
        self.motor_enabled = enable

    def SetRpmValue(self, rpm_value: float):
        self.rpm_value = min(1.0, max(0.0, rpm_value))

    def SetRpmLimitValues(self, a_lim: float, b_lim: float):
        self.rpm_setpoint_a = min(1.0, max(0.0, a_lim))
        self.rpm_setpoint_b = min(1.0, max(0.0, b_lim))

    def SetTorqueValue(self, torque_value: float):
        self.torque_value = min(1.0, max(0.0, torque_value))

    def SetTorqueLimitValues(self, a_lim: float, b_lim: float, c_lim: float):
        self.torque_setpoint_a = min(1.0, max(0.0, a_lim))
        self.torque_setpoint_b = min(1.0, max(0.0, b_lim))
        self.torque_setpoint_c = min(1.0, max(0.0, c_lim))

    def SetTorqueAlarmSelected(self, select_low: bool):
        self.torque_alarm_selected = select_low

    def SetForegroundColour(self, colour):
        """
        Sets the :class:`MotorControlRpmCurrent` foreground (text) colour.

        :param `colour`: a valid :class:`wx.Colour` object.

        :note: Overridden from :class:`wx.Control`.
        """

        wx.Control.SetForegroundColour(self, colour)
        self.Refresh()

    def SetRpmColors(self, startup: str, normal: str, alarm: str, setpoint: str):
        self.rpm_startup_color = wx.Colour(startup)
        self.rpm_normal_color = wx.Colour(normal)
        self.rpm_alarm_color = wx.Colour(alarm)
        self.rpm_setpoint_color = wx.Colour(setpoint)

    def SetTorqueColors(self, startup: str, normal: str, alarm: str, setpoint: str):
        self.torque_startup_color = wx.Colour(startup)
        self.torque_normal_color = wx.Colour(normal)
        self.torque_alarm_color = wx.Colour(alarm)
        self.torque_setpoint_color = wx.Colour(setpoint)

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
