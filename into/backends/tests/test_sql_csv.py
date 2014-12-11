from into.backends.sql_csv import *
from into import resource


def normalize(s):
    s2 = ' '.join(s.strip().split()).lower().replace('_', '')
    return s2


csv = CSV('/var/tmp/myfile.csv', delimiter=',', has_header=True)
ds = datashape.dshape('var * {name: string, amount: int}')
tbl = resource('sqlite:///:memory:::my_table', dshape=ds)


def test_postgres_load():
    assert normalize(copy_command('postgresql', tbl, csv)) == normalize(r"""
    COPY my_table from '/var/tmp/myfile.csv'
    (FORMAT csv, DELIMITER E',',
    NULL '', QUOTE '"', ESCAPE '\',
    HEADER True, ENCODING 'utf-8';
    """)


def test_sqlite_load():
    assert normalize(copy_command('sqlite', tbl, csv)) == normalize("""
     (echo '.mode csv'; echo '.import /var/tmp/myfile.csv my_table';) | sqlite3 :memory:
     """)


def test_mysql_load():
    assert normalize(copy_command('mysql', tbl, csv)) == normalize(r"""
            LOAD DATA '' INFILE '/var/tmp/myfile.csv'
            INTO TABLE my_table
            CHARACTER SET utf-8
            FIELDS
                TERMINATED BY ','
                ENCLOSED BY '"'
                ESCAPED BY '\'
            LINES TERMINATED BY '\n\r'
            IGNORE 1 LINES;""")