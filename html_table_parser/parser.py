# -----------------------------------------------------------------------------
# Name:        html_table_parser
# Purpose:     Simple class for parsing an (x)html string to extract tables.
#              Written in python3
#
# Author:      Josua Schmid
#
# Created:     05.03.2014
# Copyright:   (c) Josua Schmid 2014
# Licence:     AGPLv3
#
#
# ChangeLog:   Add logic to handle rowspan and colSpan      2019.10.24
# 
# -----------------------------------------------------------------------------

from html.parser import HTMLParser


class HTMLTableParser(HTMLParser):
    """ This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    """
    def __init__(
        self,
        decode_html_entities=False,
        data_separator=' ',
    ):

        HTMLParser.__init__(self)

        self._parse_html_entities = decode_html_entities
        self._data_separator = data_separator

        self._in_td = False
        self._in_th = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []

        # add two flag if rowspan and colspan is exited
        self.row_flag = 0
        self.col_flag = 0

    def handle_starttag(self, tag, attrs):
        """ We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        if tag == 'td':
            """这里判断有没有跨行（或跨列）的情况，并将值添加到标志位
            需要注意的是，跨行的时候，这里只处理第一列的情况，因为学籍页面只有第一列有rowspan
            其余列稍微复杂一些，就暂时不做
            """
            for i in attrs:
                if  i[0] == 'rowspan' and i[1]:
                    self.row_flag = int(i[1])
                if  i[0] == 'colspan' and i[1]:
                    self.col_flag = int(i[1])

            self._in_td = True
        if tag == 'th':
            self._in_th = True

    def handle_data(self, data):
        """ This is where we save content to a cell """
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())

    def handle_charref(self, name):
        """ Handle HTML encoded characters """

        if self._parse_html_entities:
            self.handle_data(self.unescape('&#{};'.format(name)))

    def handle_endtag(self, tag):
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False

        if tag in ['td', 'th']:
            final_cell = self._data_separator.join(self._current_cell).strip()
            self._current_row.append(final_cell)
        
            """跨列的时候，旁边的相应列补上 '-', 表示跨列
            """
            if self.col_flag:
                for i in range(self.col_flag - 1):
                    self._current_row.append('-')
                self.col_flag = 0
            
            self._current_cell = []

        elif tag == 'tr':
            self._current_table.append(self._current_row)
            self._current_row = []

            """首列跨行，所以就在第二行开始初始化一个 '-'
            """
            if self.row_flag - 1 >= 1:
                self._current_row = ['-']
                self.row_flag = self.row_flag - 1

        elif tag == 'table':
            self.tables.append(self._current_table)
            self._current_table = []
