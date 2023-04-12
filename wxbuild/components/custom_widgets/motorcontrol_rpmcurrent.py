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

        self.rpm_value = 0
        self.rpm_setpoint_a = 0.3
        self.rpm_setpoint_b = 0.8
        self.torque_value = 0
        self.torque_setpoint_a = 0.3
        self.torque_setpoint_b = 0.7
        self.torque_setpoint_c = 0.8

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(85, 40)
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
        self._disable_color_light = wx.Colour(90, 90, 90, 100)
        self._enable_color_light = wx.Colour(255, 90, 90, 200)
        self._enable_color = wx.Colour(255, 50, 50, 200)
        self._disable_color = wx.Colour(50, 50, 50, 100)
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
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()

        clientRect = self.GetClientRect()

        c0 = wx.Colour(30, 200, 40)
        # c1 = wx.Colour(30, 150, 40)
        c1 = wx.Colour(0, 40, 0)

        # xc = 5
        # yc = 5
        # r0 = 10
        # r1 = 14
        #
        # # gc.AddArc(x=xc, y=yc, r=15, startAngle=0, endAngle=275, clockwise=True)
        # gc.SetBrush(wx.Brush(c1))
        # gc.DrawEllipse(x=xc, y=yc, w=r1, h=r1)
        # gc.DrawEllipse(x=xc, y=yc+20, w=r1, h=r1)
        #
        # gc.SetBrush(wx.Brush(c0))
        # gc.DrawEllipse(x=xc + 2, y=yc + 2, w=r0, h=r0)
        # gc.SetBrush(wx.Brush(wx.WHITE))
        # gc.DrawEllipse(x=xc + 2, y=yc + 22, w=r0, h=r0)

        gc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255), width=1, style=wx.PENSTYLE_SOLID))
        gc.SetBrush(wx.Brush(wx.CYAN))

        x = 3
        y = 5
        w = 15
        h = 15
        radius = 5
        gc.DrawRoundedRectangle(x, y, w, h, radius)
        gc.DrawRoundedRectangle(x, y + 18, w, h, radius)

        x = 13
        y = 9
        w = 70
        h = 8
        gc.DrawRectangle(x, y, w, h)
        gc.DrawRectangle(x, y + 18, w, h)

        gc.SetBrush(wx.Brush(wx.RED))
        x = 60
        y = 9
        w = 2
        h = 16
        gc.DrawRectangle(x, y - 5, w, h)
        gc.DrawRectangle(x - 30, y + 18 - 5, w, h)


        gc.SetPen(wx.Pen(wx.Colour(0,0,0,0)))
        gc.SetBrush(wx.Brush(wx.Colour(255,0,0,50)))
        path = gc.CreatePath()
        path.AddCircle(50.0, 50.0, 50.0)
        path.MoveToPoint(0.0, 50.0)
        path.AddLineToPoint(100.0, 50.0)
        path.MoveToPoint(50.0, 0.0)
        path.AddLineToPoint(50.0, 100.0)
        path.CloseSubpath()
        path.AddRectangle(25.0, 25.0, 50.0, 50.0)

        # gc.StrokePath(path)
        gc.DrawPath(path)

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


    def SetForegroundColour(self, colour):
        """
        Sets the :class:`MotorControlRpmCurrent` foreground (text) colour.

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
