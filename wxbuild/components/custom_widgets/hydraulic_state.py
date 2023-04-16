# --------------------------------------------------------------------------------- #
# MOTOR CONTROL RPM AND TORQUE CURRENT wxPython IMPLEMENTATION
#
# Kristian Borve, @ 12 April 2023
# Latest Revision: 12 April 2023
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wxbuild.components.custom_widgets.hydraulic_state.HydraulicStateDisplay` is another
custom-drawn data info class


Description
===========

:class:`HydraulicStateDisplay` is another custom-drawn info class

"""

import wx


HOVER = 1
""" Flag used to indicate that the mouse is hovering on a :class:`HydraulicStateDisplay`. """


class HydraulicStateDisplay(wx.Control):
    """ This is the main class implementation of :class:`HydraulicStateDisplay`. """

    def __init__(self, parent, id=wx.ID_ANY, bitmap=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, align=wx.CENTER, validator=wx.DefaultValidator,
                 name="hydraulicstatedisplay"):
        """
        Default class constructor.

        :param `parent`: the :class:`HydraulicStateDisplay` parent;
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
        self.p_animation_value = 0.99
        self.p_value = 0.4
        self.p_setpoint = 0.7
        self.p_real_value = 1250
        self.p_setpoint_real_value = 5231
        #
        self.sov1_open = False
        self.sov2_open = True
        #
        # self.arm_in_color = self.GetParent().GetBackgroundColour()
        # self.arm_in_color = wx.Colour('#69817f')
        # self.arm_moving_color = wx.Colour('#afd9ff')
        # self.arm_out_color = wx.Colour('#a3f3a1')
        self.pressure_setpoint_color = wx.Colour('#0028a6')

        self._mouseAction = None
        self.SetBitmapLabel(bitmap)
        self._hasFocus = False

        self._alignment = align

        self.InheritAttributes()
        size = wx.Size(120, 27)
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
        self._enable_color = wx.Colour(90, 90, 255, 255)
        self._disable_color = wx.Colour(200, 200, 200, 255)
        self._no_color = wx.Colour(0, 0, 0, 0)

        self.arm_in_color = self._disable_color_light
        self.arm_moving_color = wx.Colour('#afd9ff')
        self.arm_out_color = self._enable_color

    def SetPressureValues(self, value=None, setpoint=None, setpoint_real_value=None,
                          real_value=None, animation_value=None):
        if value is not None:
            self.p_value = value
        if setpoint is not None:
            self.p_setpoint = setpoint
        if real_value is not None:
            self.p_real_value = real_value
        if animation_value is not None:
            self.p_animation_value = animation_value
        if setpoint_real_value is not None:
            self.p_setpoint_real_value = setpoint_real_value
        self.Refresh()

    def SetSovValues(self, sov1_value=None, sov2_value=None):
        if sov1_value is not None:
            self.sov1_open = sov1_value
        if sov2_value is not None:
            self.sov2_open = sov2_value
        self.Refresh()

    def SetWidgetEnable(self, enable: bool):
        self.widget_enabled = enable
        self.Refresh()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`HydraulicStateDisplay`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        event.Skip()
        self.Refresh()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`HydraulicStateDisplay`.

        :param `event`: a :class:`PaintEvent` event to be processed.
        """

        dc = wx.BufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        # dc.SetBackground(wx.Brush(wx.Colour(230, 230, 255, 155)))
        dc.Clear()

        clientRect = self.GetClientRect()
        x0, y0, w_, h_ = clientRect
        # w = w_*0.99

        font_pixel_size = 7
        font = wx.Font(wx.FontInfo(font_pixel_size).Bold())
        gc.SetFont(font, wx.Colour(0, 0, 0, 255))

        # txt_pos = (0, 0.25, 0.4, 0.6, 0.85)
        # for i, txt_str in enumerate(['Sov1', '⚓', 'Tx', 'Sov2', 'Rx']):  # '⚓'
        #     pass
        #     gc.DrawText(str=txt_str, x=txt_pos[i]*w, y=y0 + h_ * 0.1, )

        paths = []
        brushes = []
        pens = []

        if self.widget_enabled:
            gc.SetFont(font, wx.Colour(0, 0, 0, 255))
            crosshair_pen = wx.Pen(wx.Colour(0, 0, 0, 255), width=1, style=wx.PENSTYLE_SOLID)
            # sov_open_brush = wx.Brush(wx.Colour('#C3FFD6'))
            # sov_close_brush = wx.Brush(wx.Colour('#ffc7b8'))
            sov_open_brush = wx.Brush(wx.Colour('#ffffff'))
            sov_close_brush = wx.Brush(wx.Colour('#8bb3ff'))
            #
            arm_in_color = self.arm_in_color
            arm_moving_color = self.arm_moving_color
            arm_out_color = self.arm_out_color
            #
            hydr_pen = wx.Pen(wx.Colour(0, 0, 0, 255), width=1, style=wx.PENSTYLE_SOLID)
        else:
            gc.SetFont(font, wx.Colour(0, 0, 0, 150))
            crosshair_pen = wx.Pen(wx.Colour(0, 0, 0, 150), width=1, style=wx.PENSTYLE_SOLID)
            # sov_open_brush = wx.Brush(wx.Colour(0, 0, 0, 150))
            # sov_close_brush = wx.Brush(wx.Colour(0, 0, 0, 150))
            sov_open_brush = wx.Brush(self._disable_color_light)
            sov_close_brush = wx.Brush(self._disable_color_light)
            #
            arm_in_color = self._disable_color_light
            arm_moving_color = self._disable_color_light
            arm_out_color = self._disable_color_light
            #
            hydr_pen = wx.Pen(wx.Colour(0, 0, 0, 255), width=1, style=wx.PENSTYLE_SOLID)

        y_hc = h_*0.3
        sov_r = w_*0.025
        sov_open_offset = h_*0.1

        # ---- Create solenoid 1 valve --------------------------------------------
        x = sov_r*1.5
        if self.sov1_open:
            y = y_hc - sov_open_offset
            rect_brush = sov_open_brush
        else:
            y = y_hc
            rect_brush = sov_close_brush

        path, path_r = self._draw_sov_path(x, sov_r, y, y_hc, h_, gc)

        #
        paths.append(path_r)
        paths.append(path)
        brushes.append(rect_brush)
        brushes.append(wx.Brush(self._no_color))  # _disable_color_very_light
        pens.append(hydr_pen)
        pens.append(None)

        # ---- Create solenoid 2 valve --------------------------------------------
        x = sov_r * 1.5 + w_*0.6
        if self.sov2_open:
            y = y_hc - sov_open_offset
            rect_brush = sov_open_brush
        else:
            y = y_hc
            rect_brush = sov_close_brush

        path, path_r = self._draw_sov_path(x, sov_r, y, y_hc, h_, gc)
        #
        paths.append(path_r)
        paths.append(path)
        brushes.append(rect_brush)
        brushes.append(wx.Brush(self._no_color))  # _disable_color_very_light
        pens.append(hydr_pen)
        pens.append(None)

        # ----- Create Arm animation -----------------------------------------------
        x_anim = x - sov_r * 1.5
        dx1 = x_anim - sov_r * 3.2
        #
        xx0 = sov_r * 3.2
        xx1 = xx0 + dx1/9 * 1
        xx2 = xx0 + dx1/9 * 2
        xx3 = xx0 + dx1/9 * 3
        xx4 = xx0 + dx1/9 * 4
        xx5 = xx0 + dx1/9 * 5
        xx6 = xx0 + dx1/9 * 6
        xx7 = xx0 + dx1/9 * 7
        xx8 = xx0 + dx1/9 * 8
        xx9 = x_anim
        # To Sov 2 box
        xx10 = xx9 + sov_r * 3.2
        xx11 = xx10 + dx1/9 * 1
        xx12 = xx10 + dx1/9 * 2
        xx13 = xx10 + dx1/9 * 3
        xx14 = xx10 + dx1/9 * 4
        xx15 = xx10 + dx1/9 * 5
        yy0 = y_hc + h_ * 0.1 + sov_r * 1.0
        yy1 = yy0 - y_hc * min(1.0, self.p_animation_value*3)
        yy2 = yy0 - y_hc * min(1.0, max(0.0, self.p_animation_value-1/3)*3)
        yy3 = yy0 - y_hc * min(1.0, max(0.0, self.p_animation_value-2/3)*3)

        x_arr = [
            xx0,
            xx1,
            xx2,
            xx3,
            xx4,
            xx5,
            xx6,
            xx7,
            xx8,
            xx9,
            None,
            xx10,
            xx11,
            xx12,
            xx13,
            xx14,
            xx15,
        ]
        y_arr = [
            yy0,
            yy0,
            yy1,
            yy1,
            yy0,
            yy0,
            yy2,
            yy2,
            yy0,
            yy0,
            None,
            yy0,
            yy0,
            yy3,
            yy3,
            yy0,
            yy0,
        ]

        path = gc.CreatePath()
        next_do_move = True
        for i, x_ in enumerate(x_arr):
            if x_ is None:
                next_do_move = True
            else:
                if next_do_move:
                    next_do_move = False
                    path.MoveToPoint(x_, y_arr[i])
                else:
                    path.AddLineToPoint(x_, y_arr[i])

        x_arr.reverse()
        y_arr.reverse()
        next_do_move = False
        for i, x_ in enumerate(x_arr):
            if x_ is None:
                next_do_move = True
            else:
                if next_do_move:
                    next_do_move = False
                    path.MoveToPoint(x_, y_arr[i] - sov_r*0.9)
                else:
                    path.AddLineToPoint(x_, y_arr[i] - sov_r*0.9)

        paths.append(path)
        brushes.append(wx.Brush(self._no_color))  # _disable_color_very_light
        pens.append(hydr_pen)

        # ---- Add color to moving parts -------------------------------
        x_arr.reverse()
        y_arr.reverse()
        x_arr_fill_args = [
            (1, 5,),
            (5, 9,),
            (12, 16,),
        ]
        fill_colors = []
        for i in range(3):
            norm_val = max(self.p_animation_value - 1/3*i, 0)
            if norm_val < 0.001:
                fill_colors.append(arm_in_color)
            elif norm_val < 1/3:
                fill_colors.append(arm_moving_color)
            else:
                fill_colors.append(arm_out_color)

        for i, (start_arg, end_arg) in enumerate(x_arr_fill_args):
            path = gc.CreatePath()
            path.MoveToPoint(x_arr[start_arg], y_arr[start_arg])
            for j in range(start_arg+1, end_arg, 1):
                path.AddLineToPoint(x_arr[j], y_arr[j])
            for j_ in range(end_arg-1, start_arg-1, -1):
                path.AddLineToPoint(x_arr[j_], y_arr[j_] - sov_r*0.9)

            paths.append(path)
            brushes.append(wx.Brush(fill_colors[i]))  # _disable_color_very_light
            pens.append(wx.Pen(self._no_color))



        # ---- Create Pressure bar -----------------------------------------------
        x_bar = x0
        y_bar = y0 + h_*0.8
        bar_height = h_*0.2
        bar_width = w_ * 0.65
        #
        bar_width_part1 = self.p_value * bar_width
        bar_width_part2 = bar_width - bar_width_part1

        path1 = gc.CreatePath()
        path1.AddRectangle(x=x_bar, y=y_bar, w=bar_width_part1, h=bar_height)
        path2 = gc.CreatePath()
        path2.AddRectangle(x=x_bar + bar_width_part1, y=y_bar, w=bar_width_part2, h=bar_height)

        paths.append(path1)
        paths.append(path2)
        brushes.append(wx.Brush(arm_out_color))
        brushes.append(wx.Brush(self._disable_color_very_light))
        pens.append(wx.TRANSPARENT_PEN)
        pens.append(None)

        # -- Add pressure limit setpoint
        if self.widget_enabled:
            if self.p_setpoint > 0.0:
                path3 = gc.CreatePath()
                path3.AddRectangle(x=self.p_setpoint*bar_width, y=y_bar, w=1, h=bar_height)

                pens.append(None)
                brushes.append(wx.Brush(self.pressure_setpoint_color))
                paths.append(path3)

        # Draw pressure value text
        # font_pixel_size = 7
        # font = wx.Font(wx.FontInfo(font_pixel_size).Bold())
        # gc.SetFont(font, wx.Colour(0, 0, 0, 255))
        txt_str = f"{self.p_real_value:.1f} bar"
        gc.DrawText(str=txt_str, x=bar_width, y=y_bar - h_*0.15)

        for i in range(len(paths)):
            if pens[i] is not None:
                gc.SetPen(pens[i])
            if brushes[i] is not None:
                gc.SetBrush(brushes[i])
            gc.DrawPath(paths[i])

    def _draw_sov_path(self, x, sov_r, y, y_hc, h_, gc):
        xr = x - sov_r * 1.5
        xx0 = x - sov_r * 1.3
        xx1 = x
        xx2 = x + sov_r * 1.3
        yy0 = y_hc + h_ * 0.1
        yy1 = yy0 + sov_r * 1.0
        yy2 = yy1 + sov_r * 1.15

        path_r = gc.CreatePath()
        path_r.AddRectangle(x=xr, y=0, w=sov_r * 3.2, h=yy2)

        path = gc.CreatePath()
        path.AddCircle(x=x, y=y, r=sov_r)
        #
        path.MoveToPoint(xx0, yy0)
        path.AddLineToPoint(xx1, yy1)
        path.AddLineToPoint(xx1, yy2)
        path.MoveToPoint(xx1, yy1)
        path.AddLineToPoint(xx2, yy0)
        path.MoveToPoint(x, 0)
        path.AddLineToPoint(x, y - sov_r)

        return path, path_r

    def OnMouseEnter(self, event):
        """
        Handles the ``wx.EVT_ENTER_WINDOW`` event for :class:`HydraulicStateDisplay`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if not self.IsEnabled():
            return

        self._mouseAction = HOVER
        self.Refresh()
        event.Skip()

    def OnMouseLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for :class:`HydraulicStateDisplay`.

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
