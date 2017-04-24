# -*- coding: utf-8 -*-
from lib import *
import os
from lib.exceptions import *
import time

mysql = mysql('mp_info')

mysql.tables('mp_info')
mysql.where_sql = ' is_py > 0 '
mysql.save({'is_py':0})
