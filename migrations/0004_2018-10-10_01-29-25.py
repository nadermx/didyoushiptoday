# -*- coding: utf-8 -*-
# Generated by Pony ORM 0.8-dev on 2018-10-10 01:29
from __future__ import unicode_literals

from pony import orm
from pony.migrate import diagram_ops as op

dependencies = ['0003_2018-09-23_22-50-22']

operations = [
    op.AddAttr('Ship', 'ip_address', orm.Optional(str, sql_default="''"))]