import pandas as pd
import sqlite3
from sqlalchemy import create_engine


class Model():
	def __init__(self):
		self.conn = create_engine('mysql://root@localhost/classicmodels')

	def read(self):
		self.data = pd.read_sql_query('SELECT * FROM `customers`;', self.conn)
		self.df = pd.DataFrame(self.data)
		return self.df

