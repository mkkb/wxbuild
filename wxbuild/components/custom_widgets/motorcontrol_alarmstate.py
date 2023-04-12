# --------------------------------------------------------------------------------- #
# MOTOR CONTROL RPM AND TORQUE CURRENT wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.motorcontrol_alarmstate.MotorControlAlarmState` is another
custom-drawn data info class


Description
===========

:class:`MotorControlAlarmState` is another custom-drawn info class

"""

import wx
from enum import IntFlag, auto


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`MotorControlAlarmState`. """
CLICK = 2
""" Flag used to indicate that the :class:`MotorControlAlarmState` is on a pressed state. """


class MotorAlarmStatesEnum(IntFlag):
    ALARM_0 = auto()
    ALARM_1 = auto()
    ALARM_2 = auto()
    ALARM_3 = auto()
    ALARM_4 = auto()
    ALARM_5 = auto()
    ALARM_6 = auto()
    ALARM_7 = auto()
    ALARM_8 = auto()


class MotorControlAlarmStateEvent(wx.PyCommandEvent):
    """ Event sent from :class:`MotorControlAlarmState` when the button is activated. """

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

        :param `btn`: the button object, an instance of :class:`MotorControlAlarmState`.
        """

        self.theButton = btn


    def GetButtonObj(self):
        """ Returns the object associated with this event. """

        return self.theButton


class MotorControlAlarmState(wx.Control):
    """ This is the main class implementation of :class:`MotorControlAlarmStateEvent`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="motorcontrolalarmstate"):
        """
        Default class constructor.

        :param `parent`: the :class:`MotorControlAlarmState` parent;
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

        self.possible_states = MotorAlarmStatesEnum
        self.state = 0

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(40, 27)
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
        Handles the ``wx.EVT_PAINT`` event for :class:`MotorControlDriveState`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        # dc.SetBackground(wx.Brush(wx.Colour(200, 200, 255, 255)))
        dc.Clear()

        clientRect = self.GetClientRect()
        # gradientRect = wx.Rect(*clientRect)
        # capture = wx.Window.GetCapture()

        # print(" Client rect: ", clientRect, self._mouseAction, " | ", clientRect.width, clientRect.height)
        x0, y0, w_, h_ = clientRect

        if self._mouseAction == HOVER:
            hover_extra = (clientRect[3] * 0.03) / 2
            enable_color = self._enable_color_light
            disable_color = self._disable_color_light
        else:
            hover_extra = 0
            enable_color = self._enable_color
            disable_color = self._disable_color

        r0 = (clientRect[3] * 0.85) / 2 + hover_extra
        r1 = (clientRect[3] * 0.1) / 2 + hover_extra

        x = x0 + 3 + r0*0.7 - hover_extra
        y = y0 + 1 + r0 - hover_extra

        y1 = h_ - r0*0.7

        y2 = y1 - r0*0.5
        y3 = y1 - r0*1.2

        x2 = x - r0*0.05
        x3 = x - r0 * 0.25
        x4 = x + r0 * 0.25
        x5 = x + r0 * 0.05

        path1 = gc.CreatePath()
        path1.AddRoundedRectangle(x0+w_*0.05, y0+h_*0.05 - hover_extra, w_*0.9, h_*0.9 + hover_extra*2, r0/2)

        path2 = gc.CreatePath()
        path2.AddCircle(x, y1, r1)
        path2.MoveToPoint(x2, y2)
        path2.AddLineToPoint(x3, y3)
        path2.AddLineToPoint(x4, y3)
        path2.AddLineToPoint(x5, y2)
        path2.AddLineToPoint(x2, y2)

        paths = [
            path1,
            path2,
        ]

        brushes = [
            wx.Brush(wx.Colour(0, 0, 0, 0)),
        ]

        pens = [
            # wx.Pen(disable_color, width=1, style=wx.PENSTYLE_SOLID),
            wx.Pen(self._no_color, width=1, style=wx.PENSTYLE_SOLID),
        ]
        if self.state > 0:
            pens.append(wx.Pen(enable_color, width=3, style=wx.PENSTYLE_SOLID), )
            brushes.append(wx.Brush(enable_color),)
        else:
            pens.append(wx.Pen(disable_color, width=3, style=wx.PENSTYLE_SOLID), )
            brushes.append(wx.Brush(disable_color), )

        x_arr = [x + r0*0.8 + (i%3)*r0*0.45 for i in range(9)]
        y_arr = [y + r0*0.5 - r0*0.5*(i//3) for i in range(9)]
        r_arr = (1.5,)*9
        flags_arr = [
            self.possible_states(2 ** i) for i in range(len(self.GetPossibleStateNames()))
        ]

        for i in range(len(flags_arr)):
            p = gc.CreatePath()
            p.AddCircle(x=x_arr[i], y=y_arr[i], r=r_arr[i])
            if flags_arr[i] & self.state:
                pens.append(wx.Pen(enable_color, width=1, style=wx.PENSTYLE_SOLID), )
                brushes.append(wx.Brush(enable_color))
            else:
                pens.append(wx.Pen(disable_color, width=1, style=wx.PENSTYLE_SOLID), )
                brushes.append(wx.Brush(disable_color))
            paths.append(p)

        for i in range(len(paths)):
            gc.SetPen(pens[i])
            gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

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

        if self.HasCapture():
            self.ReleaseMouse()

        if rect.Contains(pos):
            self._mouseAction = HOVER
            self.Notify()
        else:
            self._mouseAction = None

        self.Refresh()
        event.Skip()

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`MotorControlAlarmStateEvent`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`MotorControlAlarmStateEvent`.

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
        Sets the :class:`MotorControlAlarmStateEvent` foreground (text) colour.

        :param `colour`: a valid :class:`wx.Colour` object.

        :note: Overridden from :class:`wx.Control`.
        """

        wx.Control.SetForegroundColour(self, colour)
        self.Refresh()

    def SetState(self, state: int):
        self.state = state
        self.Refresh()

    def GetState(self):
        return self.state

    def GetPossibleStateNames(self):
        return self.possible_states._member_names_

    def GetPossibleStateValues(self):
        return self.possible_states._value2member_map_

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

    def Notify(self):
        """ Actually sends a ``wx.EVT_BUTTON`` event to the listener (if any). """

        evt = MotorControlAlarmStateEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)
