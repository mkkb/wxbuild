from dataclasses import dataclass
import wx
import wx.richtext

import numpy as np


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

        self.text_length_shape = (450, 180)
        self.max_characters = 65_000
        self.max_character_write_per_frame = 50 * 100  # 5_000 -> 50 fps  -> 250_000

        self.insertion_pointers = []
        self.static_pre_text = []
        self.static_post_text = []
        self.dynamic_text = []

        self.rich_text_widgets = []
        self.write_pointers = []

        self.filter_masks = []

    def post_init(self):
        self.text_fonts = [
            wx.Font(
                pointSize=self.default_fontsize,
                family=wx.FONTFAMILY_MODERN, style=wx.FONTSTYLE_ITALIC, weight=wx.FONTWEIGHT_MEDIUM,
                underline=False, faceName="", encoding=wx.FONTENCODING_DEFAULT
            ),
        ]

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

        self.sizer = wx.GridSizer(self.n_rows, self.n_cols, 10, 10)
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                richtext_widget = wx.richtext.RichTextCtrl(
                    self, wx.ID_ANY, value=value, style=wx.TE_MULTILINE | wx.TE_READONLY, size=self.dataclass.size
                )
                self.sizer.Add(richtext_widget, 1, wx.ALL|wx.EXPAND, 5)

                self.rich_text_widgets.append(richtext_widget)
                self.insertion_pointers.append(0)
                self.write_pointers.append(0)
                self.dynamic_text.append([
                    np.zeros(self.text_length_shape[0], dtype=np.ubyte),    # size
                    np.zeros(self.text_length_shape[0], dtype=bool),        # written
                    np.zeros(shape=self.text_length_shape, dtype=np.ubyte), # Ascii decoded text
                ])
                self.static_pre_text.append("")
                self.static_post_text.append("")

                # format of mask =>  ['mask_name'] : [wx.Font, color: str, bold_on, italic_on, underline_on]
                self.filter_masks.append({'default':[self.text_fonts[0], self.default_color, False, False, False]})

        self.SetSizerAndFit(self.sizer)

    def clear_displayed_text(self, widget_index=0):
        print(" clearing displayed text:: ")
        self.Freeze()
        widget = self.rich_text_widgets[widget_index]
        widget.Remove(self.insertion_pointers[widget_index], widget.GetLastPosition())
        self.Thaw()

    def clear_text(self, widget_index=0):
        print(" clearing text from buffer and display:: ")
        self.clear_displayed_text(widget_index=widget_index)

    def set_text(self, text, widget_index=0):
        print(" adding mask:: ")

    def add_to_text(self, text, widget_index=0):
        # print(" adding text:: ", text)
        format_filter = self.filter_masks[widget_index]['default']

        # Add to text buffer
        self.add_text_to_buffer(text, widget_index)

        # Extract data to insert from text buffer

        # Add formatting characters based on filters

        # Write text to into widget

        self.Freeze()
        widget = self.rich_text_widgets[widget_index]
        widget.SetInsertionPoint(self.insertion_pointers[widget_index])
        widget.BeginFont(format_filter[0])
        widget.BeginTextColour(format_filter[1])
        widget.WriteText(text=text)

        if widget.GetLastPosition() > self.max_characters:
            widget.Remove(self.max_characters, widget.GetLastPosition())

        self.Thaw()

    def add_mask(self, widget_index=0):
        print(" adding mask:: ")

    def set_static_pre_text(self, widget_index=0):
        print(" set_static_pre_text:: ")

    def set_static_post_text(self, widget_index=0):
        print(" set_static_post_text:: ")

    #
    def add_text_to_buffer(self, text : str, widget_index=0):
        # self.max_character_write_per_frame = 50 * 100 = 5_000
        # self.text_length_shape = (450, 180)  =  81_000
        max_line_width = self.text_length_shape[1]
        print(" max_lw", max_line_width)

        # text_size_map =  self.dynamic_text[widget_index][0]
        # bool_text_drawn_map = self.dynamic_text[widget_index][1]
        # text_buffer = self.dynamic_text[widget_index][2]

        text_data = np.frombuffer(text.encode('utf-8'), np.byte)
        line_feeds = np.squeeze(np.argwhere(text_data == 10))
        print(" line_feeds:", line_feeds)

        lf_pos = 0
        for i, lf_pos in enumerate(line_feeds):
            if i == 0:
                if lf_pos > 0:
                    line_text = text_data[: lf_pos]
                     
                    print(" found a line: ", i, ":", line_text.size)
            else:
                line_text = text_data[line_feeds[i-1] + 1: lf_pos]
                print(" found a line: ", i, ":", line_text.size)
        if lf_pos < text_data.size:
            line_text = text_data[lf_pos + 1: ]
            print(" found a line: ", i + 1, ":", line_text.size)
