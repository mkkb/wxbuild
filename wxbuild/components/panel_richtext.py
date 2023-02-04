from dataclasses import dataclass
import wx
import wx.richtext

import numpy as np
import logging
logger = logging.getLogger('wx_log')


@dataclass
class WxPanel:
    parent: str = 'main_frame'
    name: str = 'first_panel'
    sizer_flags: int = wx.EXPAND | wx.ALL
    sizer_proportion: float = 0
    sizer_border: int = 0
    max_character: int = 50_000,
    background_color: tuple = ()
    shape: tuple = (1, 1)
    size: tuple = (10, 10)


class RichtextPanel(wx.Panel):
    def __init__(self, parent, main_frame, **kwargs):
        self.dataclass = WxPanel
        self.main_frame = main_frame
        self.parent = parent
        if 'shape' in kwargs:
            self.n_cols, self.n_rows = kwargs.pop('shape')
        else:
            self.n_cols, self.n_rows = 1, 1

        wx.Panel.__init__(self, parent, **kwargs)

        self.default_fontsize = 10
        self.default_color = "#000000"
        self.default_bold = False
        self.default_italic = False
        self.default_underline = False
        #
        self.char_replacement = 35  # hashtag/comment sign --> #
        self.char_valid_ascii_range = (9, 126)

        self.text_length_shape = (450, 180)  #
        self.max_characters = 65_000
        self.max_line_writes_per_frame = 50  # 5_000 -> 50 fps  -> 250_000

        self.insertion_pointers = []
        self.static_pre_text = []
        self.static_post_text = []
        self.dynamic_text = []

        self.rich_text_widgets = []
        self.write_pointers = []
        self.read_pointers = []

        self.filter_masks = []

        self.text_fonts = [
            wx.Font(
                pointSize=self.default_fontsize,
                family=wx.FONTFAMILY_MODERN,
                style=wx.FONTSTYLE_NORMAL,
                weight=wx.FONTWEIGHT_MEDIUM,
                underline=False, faceName="",
                encoding=wx.FONTENCODING_DEFAULT
            ),
        ]
        self.sizer = wx.GridSizer(self.n_rows, self.n_cols, 10, 10)

    def post_init(self):
        value = """Hello this is a long text. asdw ceqsdaceq ceqc a ceqcac ec qcasc eq c ac e.
        asdawdadasdwqdad adas dqw dasdqwd ad asd qw, das dqw dasd wqd sad sad qw dasd ,asdqw das d qwdas .
         qwd asdqw dasd qkwd asd qdsad .dwq dasd     dqwdasdqw, wd sd   d sdqsaddqcq ac cascqcqea dsdwq dsad.
          awd   dasdqwdasasdq,wdwdasd asd d qwd asdqw1231d d12d 1 sd ,21d as d asd
          12d 1dqwd 21 
          12d qwd12 d12 d1
          wd2
          
          2d1
          d
          21d
          
          d
          2
          2
          1d
          2d
          
          1
          
          2d12d
          12d
          21
          d12
          d12dqwdqwwwwwwwwwwwwwwwwwwwwwdqwdqwdasdas
          dasd
          asd
          a
          w
          da
          sd
          aw
          daw
          d
          as
          da
          wd
          as
          d
          awd
          sd
          a
          w
          da
          wdw
          """

        for i in range(self.n_rows):
            for j in range(self.n_cols):
                richtext_widget = wx.richtext.RichTextCtrl(
                    self, wx.ID_ANY, value=value, style=wx.TE_MULTILINE | wx.TE_READONLY, size=self.dataclass.size
                )
                self.sizer.Add(richtext_widget, 1, wx.ALL | wx.EXPAND, 5)

                self.rich_text_widgets.append(richtext_widget)
                self.insertion_pointers.append(0)
                self.write_pointers.append(0)
                self.read_pointers.append(0)
                self.dynamic_text.append([
                    np.zeros(self.text_length_shape[0], dtype=np.ubyte),     # size
                    np.zeros(self.text_length_shape[0], dtype=bool),         # written
                    np.zeros(self.text_length_shape[0], dtype=np.uint32),    # format
                    np.zeros(shape=self.text_length_shape, dtype=np.ubyte),  # Ascii decoded text
                ])
                self.static_pre_text.append("")
                self.static_post_text.append("")

                # format of mask =>  ['mask_name'] : [wx.Font, color: str, bold_on, italic_on, underline_on]
                self.filter_masks.append({'default': [self.text_fonts[0], self.default_color, False, False, False]})

        self.SetSizerAndFit(self.sizer)

    def clear_displayed_text(self, widget_index=0):
        # logger.info(" clearing displayed text:: ")
        self.Freeze()
        widget = self.rich_text_widgets[widget_index]
        widget.Remove(self.insertion_pointers[widget_index], widget.GetLastPosition())
        self.dynamic_text[widget_index][1][:] = False
        self.Thaw()

    def clear_text(self, widget_index=0):
        logger.info(" clearing text from buffer and display:: ")
        self.clear_displayed_text(widget_index=widget_index)
        self.dynamic_text[widget_index][0][:] = 0

    def add_to_text(self, text, widget_index=0):
        self._add_text_to_buffer(text, widget_index)
        self._write_text_to_widget_from_buffer(widget_index)

    def add_mask(self, widget_index=0):
        logger.info(" adding mask:: ")

    def set_static_pre_text(self, widget_index=0):
        logger.info(" set_static_pre_text:: ")

    def set_static_post_text(self, widget_index=0):
        logger.info(" set_static_post_text:: ")

    def set_configuration(self, max_line_writes_per_frame=50, max_characters=50_000, text_length_shape=(450, 180)):
        self.max_line_writes_per_frame = max_line_writes_per_frame
        self.text_length_shape = text_length_shape
        self.max_characters = max_characters

    def update_widget(self):
        for i in range(len(self.dynamic_text)):
            self._write_text_to_widget_from_buffer(widget_index=i)

    #
    def _add_text_to_buffer(self, text: str, widget_index=0):
        max_line_width = self.text_length_shape[1]
        text_data = np.frombuffer(text.encode('utf-8'), np.byte)
        line_feed_args = np.squeeze(np.argwhere(text_data == 10))
        if line_feed_args.ndim == 0:
            line_feed_args = np.array((line_feed_args,), dtype=np.ubyte)

        lf_pos = 0
        for i, lf_pos in enumerate(line_feed_args):
            if i == 0:
                if lf_pos > 0:
                    line_text = text_data[: lf_pos]
                    self._add_single_text_line_to_buffer(line_text[:max_line_width], widget_index)
                    #
                    # print(" found a line: ", i, ":", line_text.size, lf_pos, "  (i==0, lf_pos > 0)")
            else:
                line_text = text_data[line_feed_args[i-1] + 1: lf_pos]
                self._add_single_text_line_to_buffer(line_text[:max_line_width], widget_index)
                # print(" found a line: ", i, ":", line_text.size, lf_pos, "  (i>0")
        if lf_pos < text_data.size:
            line_text = text_data[lf_pos + 1:]
            self._add_single_text_line_to_buffer(line_text[:max_line_width], widget_index)
            # print(" found a line: ", i + 1, ":", line_text.size, lf_pos, "  (lf_pos < text_data.size)")

    def _add_single_text_line_to_buffer(self, text_line: np.array, widget_index=0) -> None:
        format_int = self._filter_line_text_with_masks(text_line)

        text_size_map =  self.dynamic_text[widget_index][0]
        bool_text_drawn_map = self.dynamic_text[widget_index][1]
        text_format_map = self.dynamic_text[widget_index][2]
        text_buffer = self.dynamic_text[widget_index][3]  # shape=self.text_length_shape

        text_size_map[0] = text_line.size
        bool_text_drawn_map[0] = False
        text_format_map[0] = format_int
        text_buffer[0, :text_line.size] = text_line[:]
        self.dynamic_text[widget_index][0] = np.roll(text_size_map, -1)
        self.dynamic_text[widget_index][1] = np.roll(bool_text_drawn_map, -1)
        self.dynamic_text[widget_index][2] = np.roll(text_format_map, -1)
        self.dynamic_text[widget_index][3] = np.roll(text_buffer, -1, axis=0)

    def _write_text_to_widget_from_buffer(self, widget_index=0):
        text_size_map =  self.dynamic_text[widget_index][0][::-1]
        bool_is_text_drawn_map = self.dynamic_text[widget_index][1][::-1]
        text_format_map = self.dynamic_text[widget_index][2][::-1]
        text_buffer = self.dynamic_text[widget_index][3][::-1, :]
        n_lines_to_draw_max = self.max_line_writes_per_frame

        widget = self.rich_text_widgets[widget_index]
        i = 0
        lines_drawn = 0
        jumped_over_text = False
        write_pointer = self.insertion_pointers[widget_index]
        text_format_int = text_format_map[0]

        self.Freeze()
        widget.SetInsertionPoint(write_pointer)
        self._set_insertion_text_format(widget, text_format_int)
        while lines_drawn < n_lines_to_draw_max:
            if text_size_map[i] > 0:
                drawn = bool_is_text_drawn_map[i]
                if not drawn:
                    if jumped_over_text:
                        widget.SetInsertionPoint(write_pointer)

                    if text_format_int != text_format_map[i]:
                        text_format_int = text_format_map[i]
                        self._set_insertion_text_format(widget, text_format_int)
                    elif jumped_over_text:
                        self._set_insertion_text_format(widget, text_format_int)

                    text = text_buffer[i, :text_size_map[i]].tobytes().decode('utf-8') + "\n"
                    widget.WriteText(text=text)
                    lines_drawn += 1
                    bool_is_text_drawn_map[i] = True
                    jumped_over_text = False
                else:
                    write_pointer += text_size_map[i] + 1
                    jumped_over_text = True

            i += 1
            if i == text_size_map.size:
                break

        self.dynamic_text[widget_index][1][:] = bool_is_text_drawn_map[::-1]
        if widget.GetLastPosition() > self.max_characters:
            widget.Remove(self.max_characters, widget.GetLastPosition())

        widget.EndFont()
        widget.EndTextColour()

        self.Thaw()

    def _set_insertion_text_format(self, widget, text_format_int: int) -> None:
        if text_format_int == 0:
            widget.BeginFont(self.text_fonts[0])
            widget.BeginTextColour(wx.BLACK)

    def _filter_line_text_with_masks(self, text_line: np.array) -> int:
        return 0