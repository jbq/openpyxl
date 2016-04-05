from __future__ import absolute_import
# Copyright (c) 2010-2016 openpyxl

import pytest

from openpyxl.utils.indexed_list import IndexedList
from openpyxl.styles.styleable import StyleArray

from openpyxl.xml.functions import tostring
from openpyxl.tests.helper import compare_xml


class DummyWorkbook:

    def __init__(self):
        self.shared_styles = IndexedList()
        self._cell_styles = IndexedList()
        self._cell_styles.add(StyleArray())
        self._cell_styles.add(StyleArray([10,0,0,0,0,0,0,0,0,0]))
        self.sheetnames = []


class DummyWorksheet:

    def __init__(self):
        self.parent = DummyWorkbook()


def test_dimension_interface():
    from .. dimensions import Dimension
    d = Dimension(1, True, 1, False, DummyWorksheet())
    assert isinstance(d.parent, DummyWorksheet)
    assert dict(d) == {'hidden': '1', 'outlineLevel': '1'}


def test_invalid_dimension_ctor():
    from .. dimensions import Dimension
    with pytest.raises(TypeError):
        Dimension()


@pytest.mark.parametrize("key, value, expected",
                         [
                             ('ht', 1, {'ht':'1', 'customHeight':'1'}),
                             ('_font_id', 10, {'s':'1', 'customFormat':'1'}),
                             ('thickBot', True, {'thickBot':'1'}),
                             ('thickTop', True, {'thickTop':'1'}),
                         ]
                         )
def test_row_dimension(key, value, expected):
    from .. dimensions import RowDimension
    rd = RowDimension(worksheet=DummyWorksheet())
    setattr(rd, key, value)
    assert dict(rd) == expected


@pytest.mark.parametrize("key, value, expected",
                         [
                             ('width', 1, {'width':'1', 'customWidth':'1'}),
                             ('bestFit', True, {'bestFit':'1'}),
                         ]
                         )
def test_col_dimensions(key, value, expected):
    from .. dimensions import ColumnDimension
    cd = ColumnDimension(worksheet=DummyWorksheet())
    setattr(cd, key, value)
    assert dict(cd) == expected

def test_group_columns_simple():
    from ..worksheet import Worksheet
    ws = Worksheet(DummyWorkbook())
    dims = ws.column_dimensions
    dims.group('A', 'C', 1)
    assert len(dims) == 1
    group = list(dims.values())[0]
    assert group.outline_level == 1
    assert group.min == 1
    assert group.max == 3


def test_group_columns_collapse():
    from ..worksheet import Worksheet
    ws = Worksheet(DummyWorkbook())
    dims = ws.column_dimensions
    dims.group('A', 'C', 1, hidden=True)
    group = list(dims.values())[0]
    assert group.hidden


def test_column_dimension():
    from ..worksheet import Worksheet
    from .. dimensions import ColumnDimension
    ws = Worksheet(DummyWorkbook())
    cols = ws.column_dimensions
    assert isinstance(cols['A'], ColumnDimension)


def test_row_dimension():
    from ..worksheet import Worksheet
    from ..dimensions import RowDimension
    ws = Worksheet(DummyWorkbook())
    row_info = ws.row_dimensions
    assert isinstance(row_info[1], RowDimension)


@pytest.fixture
def ColumnDimension():
    from ..dimensions import ColumnDimension
    return ColumnDimension


def test_col_reindex(ColumnDimension):
    cd = ColumnDimension(DummyWorksheet(), index="D")
    assert dict(cd) == {}
    cd.reindex()
    assert dict(cd) == {'max': '4', 'min': '4'}


def test_col_width(ColumnDimension):
    cd = ColumnDimension(DummyWorksheet(), index="A", width=4)
    cd.reindex()
    col = cd.to_tree()
    xml = tostring(col)
    expected = """<col width="4" min="1" max="1" customWidth="1" />"""
    diff = compare_xml(xml, expected)
    assert diff is None, diff


def test_col_style(ColumnDimension):
    from ..worksheet import Worksheet
    from openpyxl import Workbook
    from openpyxl.styles import Font

    ws = Worksheet(Workbook())
    cd = ColumnDimension(ws, index="A")
    cd.font = Font(color="FF0000")
    cd.reindex()
    col = cd.to_tree()
    xml = tostring(col)
    expected = """<col max="1" min="1" style="1" />"""
    diff = compare_xml(xml, expected)
    assert diff is None, diff


def test_outline_cols(ColumnDimension):
    ws = DummyWorksheet()
    cd = ColumnDimension(ws, index="B", outline_level=1)
    cd.reindex()
    col = cd.to_tree()
    xml = tostring(col)
    expected = """<col max="2" min="2" outlineLevel="1"/>"""
    diff = compare_xml(expected, xml)
    assert diff is None, diff


def test_no_cols():
    from ..dimensions import DimensionHolder
    dh = DimensionHolder(None)
    node = dh.to_tree()
    assert node is None
