# --------------------------------------------------------------------------------- #
# MOTOR CONTROL RPM AND TORQUE CURRENT wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.rotational_state.RotationalStateDisplay` is another
custom-drawn data info class


Description
===========

:class:`RotationalStateDisplay` is another custom-drawn info class

"""

import wx
import numpy as np


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`RotationalStateDisplay`. """


class RotationalStateDisplay(wx.Control):
    """ This is the main class implementation of :class:`RotationalStateDisplay`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="rotationalstatedisplay"):
        """
        Default class constructor.

        :param `parent`: the :class:`RotationalStateDisplay` parent;
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

        self.widget_enabled = False
        self.r_value = 0.9
        self.r_real_value = 1250
        self.r_setpoint = 5231
        #
        self.rotation_big_marker_step = 2*np.pi/7/6
        self.rotation_small_markers_per_big = 4
        self.big_markers_in_view = 4
        self.rotation_view_size = self.rotation_big_marker_step*self.big_markers_in_view
        self.rotation_range_full = 2*np.pi
        #
        self.marker_labels = [i - 6 for i in range(int(self.rotation_range_full/self.rotation_big_marker_step) + 1)]

        #
        # self.crosshair_color = wx.Colour('#a9f5ff')
        # self.setpoint_color = wx.Colour('#a9f5ff')

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(80, 27)
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
        self._disable_color_very_light = wx.Colour(180, 180, 180, 255)
        self._disable_color_light = wx.Colour(90, 90, 90, 255)
        self._enable_color_light = wx.Colour(255, 90, 90, 255)
        self._enable_color = wx.Colour(255, 50, 50, 255)
        self._disable_color = wx.Colour(200, 200, 200, 255)
        self._no_color = wx.Colour(0, 0, 0, 0)

    def SetWidgetEnable(self, enable: bool):
        self.widget_enabled = enable
        self.Refresh()

    def SetRotationValues(self, value=None, setpoint=None, real_value=None):
        if value is not None:
            self.r_value = value
        if setpoint is not None:
            self.r_setpoint = setpoint
        if real_value is not None:
            self.r_real_value = real_value
        self.Refresh()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`RotationalStateDisplay`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`RotationalStateDisplay`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        # dc.SetBackground(wx.Brush(wx.Colour(230, 230, 255, 155)))
        dc.Clear()

        clientRect = self.GetClientRect()
        x0, y0, w_, h_ = clientRect
        w = w_*0.99

        paths = []
        brushes = []
        pens = []

        font_pixel_size = 6
        font = wx.Font(wx.FontInfo(font_pixel_size).Bold())
        if self.widget_enabled:
            gc.SetFont(font, wx.Colour(0, 0, 0, 255))
            crosshair_pen = wx.Pen(wx.Colour(0, 0, 0, 255), width=1, style=wx.PENSTYLE_SOLID)
            crosshair_brush = wx.Brush(wx.Colour(0, 0, 0, 255))
            # crosshair_pen_extra =  wx.Pen(wx.BLACK, width=1, style=wx.PENSTYLE_SOLID)
        else:
            gc.SetFont(font, wx.Colour(0, 0, 0, 150))
            crosshair_pen = wx.Pen(wx.Colour(0, 0, 0, 150), width=1, style=wx.PENSTYLE_SOLID)
            crosshair_brush = wx.Brush(wx.Colour(0, 0, 0, 150))
            # crosshair_pen_extra = crosshair_pen

        # if self._mouseAction == HOVER:
        #     #
        #     hover_extra = (h_ * 0.03) / 2
        # else:
        #     #
        #     hover_extra = 0

        # Calculate marker positions
        start_pos_of_view = self.r_value - self.rotation_view_size / 2

        #
        big_marker_step = self.rotation_big_marker_step / self.rotation_view_size * w
        cross_hair_offset = self.rotation_view_size / 2 - (start_pos_of_view % self.rotation_big_marker_step) \
                            / self.rotation_big_marker_step * big_marker_step
        n_big_marks = (start_pos_of_view / self.rotation_big_marker_step)

        x_increment = w * (self.rotation_big_marker_step / self.rotation_view_size)
        x_sub_incerement = x_increment / (self.rotation_small_markers_per_big + 1)

        # Create startup circle
        path1 = gc.CreatePath()
        path1.AddRoundedRectangle(x=x0, y=y0, w=w, h=h_*0.6, radius=h_*0.1)
        #
        paths.append(path1)
        brushes.append(wx.Brush(self._no_color))  # _disable_color_very_light
        pens.append(wx.Pen(self._disable_color, width=1, style=wx.PENSTYLE_SOLID), )

        # Adding cross marks
        path2 = gc.CreatePath()
        path2.AddRectangle(x=x0, y=y0 + h_*0.4, w=w, h=h_*0.05)
        for i in range(-1, self.big_markers_in_view + 1):
            x0_ = cross_hair_offset + i * x_increment
            path2.AddRectangle(x=x0_, y=y0 + h_*0.1, w=h_*0.05, h=h_*0.3)

            marker_label_indx = max(0, min(int(i + n_big_marks + 1), len(self.marker_labels)-1))
            txt_str = f"{self.marker_labels[marker_label_indx]:.0f}"
            gc.DrawText(str=txt_str,
                        x=x0_ + w_*0.05,
                        y=y0 - h_*0.001, )

            for j in range(1, 1+self.rotation_small_markers_per_big):
                x_sub_0 = x0_ + j*x_sub_incerement
                path2.AddRectangle(x=x_sub_0, y=y0 + h_ * 0.29, w=int(h_ * 0.05), h=h_ * 0.1)
        #
        paths.append(path2)
        brushes.append(crosshair_brush)
        pens.append(wx.Pen(self._no_color, width=1, style=wx.PENSTYLE_SOLID), )

        # Adding cross hair
        x0_ = w_ / 2 - w_ * 0.06
        x1_ = w_ / 2 - w_ * 0.01
        x2_ = w_ / 2 + w_ * 0.01
        x3_ = w_ / 2 + w_ * 0.06
        y0_ = h_ - h_ * 0.1
        y1_ = h_ - h_ * 0.35
        y2_ = h_ - h_ * 0.5
        path1 = gc.CreatePath()
        path1.MoveToPoint(x0_, y0_)
        path1.AddLineToPoint(x1_, y1_)
        path1.AddLineToPoint(x1_, y2_)
        path1.AddLineToPoint(x2_, y2_)
        path1.AddLineToPoint(x2_, y1_)
        path1.AddLineToPoint(x3_, y0_)
        path1.AddLineToPoint(x0_, y0_)

        paths.append(path1)
        brushes.append(wx.Brush(self._no_color))
        pens.append(crosshair_pen)

        # Draw actual values as text
        if self.widget_enabled:
            font_pixel_size = 7
            font = wx.Font(wx.FontInfo(font_pixel_size).Bold())
            gc.SetFont(font, wx.Colour(0, 0, 0, 255))
            txt_str = f"={self.r_real_value:.0f}"
            gc.DrawText(str=txt_str,
                        x=x0,
                        y=y0 + h_ * 0.65, )

            txt_str = f" >{self.r_setpoint:.0f}"
            gc.DrawText(str=txt_str,
                        x=w_ / 2 + w_ * 0.1,
                        y=y0 + h_ * 0.65, )

        for i in range(len(paths)):
            if pens[i] is not None:
                gc.SetPen(pens[i])
            if brushes[i] is not None:
                gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`RotationalStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`RotationalStateDisplay`.

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
