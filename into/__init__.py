from __future__ import absolute_import, division, print_function

__all__ = """convert append resource into drop chunks Chunks discover dshape
             CSV JSON JSONLines S3""".split()

from multipledispatch import halt_ordering, restart_ordering

halt_ordering()  # Turn off multipledispatch ordering

from .utils import ignoring
from .convert import convert
from .append import append
from .resource import resource
from .directory import Directory
from .into import into
from .drop import drop
from .chunks import chunks, Chunks
from datashape import discover, dshape
import numpy as np

with ignoring(ImportError):
    from .backends.sas import sas7bdat
with ignoring(ImportError):
    from .backends.pandas import pd
with ignoring(ImportError):
    from .backends.bcolz import bcolz
with ignoring(ImportError):
    from .backends.h5py import h5py
with ignoring(ImportError):
    from .backends.hdfstore import HDFStore
with ignoring(ImportError):
    from .backends.pytables import tables
with ignoring(ImportError):
    from .backends.dynd import nd
with ignoring(ImportError):
    from .backends import sql
with ignoring(ImportError):
    from .backends import mongo
with ignoring(ImportError):
    from .backends.csv import CSV
with ignoring(ImportError):
    from .backends.json import JSON, JSONLines
with ignoring(ImportError):
    from .backends.hdfs import HDFS
with ignoring(ImportError):
    from .backends.ssh import SSH
with ignoring(ImportError):
    from .backends import sql_csv
with ignoring(ImportError):
    from .backends.aws import S3


restart_ordering()  # Restart multipledispatch ordering and do ordering

__version__ = '0.1.3'
