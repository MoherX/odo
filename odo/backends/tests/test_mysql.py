from __future__ import absolute_import, division, print_function

import pytest

pymysql = pytest.importorskip('pymysql')

from datashape import var, DataShape, Record
import itertools
from odo.backends.csv import CSV
from odo import resource, odo
import sqlalchemy
import sqlalchemy as sa
import os
import sys
import csv as csv_module
import getpass
from odo import drop, discover
from odo.utils import tmpfile


pytestmark = pytest.mark.skipif(sys.platform == 'win32',
                                reason='not well tested on win32 mysql')

username = getpass.getuser()
url = 'mysql+pymysql://{0}@localhost:3306/test'.format(username)


def create_csv(data, file_name):
    with open(file_name, 'w') as f:
        csv_writer = csv_module.writer(f)
        for row in data:
            csv_writer.writerow(row)


data = [(1, 2), (10, 20), (100, 200)]
data_floats = [(1.02, 2.02), (102.02, 202.02), (1002.02, 2002.02)]


@pytest.yield_fixture
def csv():
    with tmpfile('.csv') as fn:
        create_csv(data, fn)
        yield CSV(fn)


@pytest.yield_fixture
def fcsv():
    with tmpfile('.csv') as fn:
        create_csv(data_floats, fn)
        yield CSV(fn, columns=list('ab'))


names = ('tbl%d' % i for i in itertools.count())


@pytest.fixture
def name():
    return next(names)


@pytest.fixture(scope='module')
def engine():
    return sqlalchemy.create_engine(url)


@pytest.yield_fixture
def sql(engine, csv, name):
    dshape = discover(csv)
    dshape = DataShape(var,
                       Record([(n, typ)
                               for n, typ in zip('ab', dshape.measure.types)]))
    try:
        t = resource('%s::%s' % (url, name), dshape=dshape)
    except sqlalchemy.exc.OperationalError as e:
        pytest.skip(str(e))
    else:
        yield t
        drop(t)


@pytest.yield_fixture
def fsql(engine, fcsv, name):
    dshape = discover(fcsv)
    dshape = DataShape(var,
                       Record([(n, typ)
                               for n, typ in zip('ab', dshape.measure.types)]))
    try:
        t = resource('%s::%s' % (url, name), dshape=dshape)
    except sqlalchemy.exc.OperationalError as e:
        pytest.skip(str(e))
    else:
        yield t
        drop(t)


@pytest.fixture
def dcsv():
    this_dir = os.path.dirname(__file__)
    file_name = os.path.join(this_dir, 'dummydata.csv')
    dshape = """var * {
        Name: string,
        RegistrationDate: date,
        ZipCode: int64,
        Consts: float64
    }"""

    return CSV(file_name, dshape=dshape)


@pytest.yield_fixture
def dsql(engine, dcsv, name):
    t = resource('%s::%s' % (url, name), dshape=discover(dcsv))
    yield t
    drop(t)


def test_csv_mysql_load(sql, csv):
    engine = sql.bind
    conn = engine.raw_connection()

    cursor = conn.cursor()
    full_path = os.path.abspath(csv.path)
    load = '''LOAD DATA INFILE '{0}' INTO TABLE {1} FIELDS TERMINATED BY ','
        lines terminated by '\n'
        '''.format(full_path, sql.name)
    cursor.execute(load)
    conn.commit()


def test_simple_into(sql, csv):
    odo(csv, sql, if_exists="replace")
    assert odo(sql, list) == [(1, 2), (10, 20), (100, 200)]


def test_append(sql, csv):
    odo(csv, sql, if_exists="replace")
    assert odo(sql, list) == [(1, 2), (10, 20), (100, 200)]

    odo(csv, sql, if_exists="append")
    assert odo(sql, list) == [(1, 2), (10, 20), (100, 200),
                              (1, 2), (10, 20), (100, 200)]


def test_simple_float_into(fsql, fcsv):
    odo(fcsv, fsql, if_exists="replace")

    assert odo(fsql, list) == [(1.02, 2.02),
                               (102.02, 202.02),
                               (1002.02, 2002.02)]


def test_tryexcept_into(sql, csv):
    # uses multi-byte character and fails over to using sql.extend()
    odo(csv, sql, if_exists="replace", QUOTE="alpha", FORMAT="csv")
    assert odo(sql, list) == [(1, 2), (10, 20), (100, 200)]


@pytest.mark.xfail(raises=KeyError)
def test_failing_argument(sql, csv):
    odo(csv, sql, if_exists="replace", skipinitialspace="alpha")


def test_no_header_no_columns(sql, csv):
    odo(csv, sql, if_exists="replace")
    assert odo(sql, list) == [(1, 2), (10, 20), (100, 200)]


@pytest.mark.xfail
def test_complex_into(dsql, dcsv):
    # data from: http://dummydata.me/generate
    odo(dcsv, dsql, if_exists="replace")
    assert odo(dsql, list) == odo(dcsv, list)


def test_sql_to_csv(sql, csv):
    sql = odo(csv, sql)
    with tmpfile('.csv') as fn:
        csv = odo(sql, fn)
        assert odo(csv, list) == data
        assert discover(csv).measure.names == discover(sql).measure.names


def test_sql_select_to_csv(sql, csv):
    sql = odo(csv, sql)
    query = sa.select([sql.c.a])
    with tmpfile('.csv') as fn:
        csv = odo(query, fn)
        assert odo(csv, list) == [(x,) for x, _ in data]
