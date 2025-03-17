# Small portions of this code were generated via LLM (Qwen2.5-coder:32b). Check qwlg_importer.txt for prompts and responses.
# NOTE: MySQL database credentials and source directory information has been removed for privacy/security reasons. 
# NOTE: Fill in these values before running this script.

import os
import io
from zipfile import ZipFile
import pandas as pd
import pyarrow as pa
from pyarrow import parquet as pq
from pathlib import Path
import mysql.connector
from time import sleep

PARQUET_MAX_SIZE = 134_217_728

def list_files_in_directory(directory):

	parquet_files = []
	csv_files = []
	
	for root, _, files in os.walk(directory):
		for file in files:
			if file.endswith('.parquet'):
				parquet_files.append(os.path.join(root, file))
			elif file.endswith('.zip'):
				csv_files.append(os.path.join(root, file))
				
	return parquet_files, csv_files


def process_csv_to_parquet(zip_files, db_connector, db_cursor):

	column_names = ["trade_id","price","qty","quoteQty","time","isBuyerMaker","isBestMatch"]

	parquet_files = []
	parquet_parts = 0
	current_parquet_size = 0
	current_parquet_file = None
	current_parquet_writer = None
	
	for file in zip_files:
		zip_file = file

		sub_dir = Path(zip_file).parent

		with ZipFile(zip_file, "r") as zf: # TODO: Use pyarrow to read csv files from .zip archives directly
			csv_file = [f for f in zf.namelist() if f.endswith(".csv")]
			print(f"CSV: {csv_file}")

			#for csv_file in csv_files:
			csv_f = zf.open(csv_file[0], "r")# as csv_f:
			df = pd.read_csv(io.TextIOWrapper(csv_f, encoding="utf-8"))
			# Dynamically name columns
			df.columns = [column_names[i] for i in range(len(df.columns))]
			
			# Convert DataFrame to PyArrow Table
			table = pa.Table.from_pandas(df)
			# Write table data in batches
			for batch in table.to_batches(max_chunksize=500000):
				#TODO: convert from pyarrow to table to pandas dataframe once, rather than from df to table to df
				#print(batch)
				temp = batch.to_pandas()
				#print(temp)
				val = list(temp.itertuples(index=False, name=None)) # "INSERT" requires either tuple, or list of tuples
				sql_query = f"INSERT INTO {test_table} VALUES (%s, %s, %s, %s, %s, %s, %s)"
				db_cursor.executemany(sql_query, val)
				db_connector.commit()
				# Serialize the batch to estimate its size
				buffer = pa.BufferOutputStream()
				with pa.ipc.new_stream(buffer, batch.schema) as writer:
					writer.write_batch(batch)
				batch_size = len(buffer.getvalue())
				print(f"BATCH SIZE: {batch_size} bytes")
				if (
					current_parquet_writer is None
					or current_parquet_size + batch_size > PARQUET_MAX_SIZE
				):
					# Close the current writer if it exists
					if current_parquet_writer:
						current_parquet_writer.close()
					# Start a new Parquet file
					parquet_parts += 1
					current_parquet_file = sub_dir / f"{sub_dir.name}_part{parquet_parts}.parquet"
					parquet_files.append(current_parquet_file)
					current_parquet_writer = pq.ParquetWriter(
						current_parquet_file, table.schema, compression="snappy"
					)
					current_parquet_size = 0  # Reset size tracker
					print("RESET PQ SIZE")
				# Write the batch to the current Parquet file
				current_parquet_writer.write_table(pa.Table.from_batches([batch]))
				current_parquet_size = Path.stat(sub_dir / f"{sub_dir.name}_part{parquet_parts}.parquet").st_size
				#sleep(0.1)
				print(f"CURRENT PQ SIZE: {current_parquet_size} bytes")
				sleep(0.001) #DEBUG: Slow down import process

	# Finalize the last file
	if current_parquet_writer:
		current_parquet_writer.close()
		current_parquet_writer = None


# Example usage:
if __name__ == "__main__":
	directory_to_search = ""

	test_database = "IMPORT_TEST"
	test_table = "TICK_DATA_TEST"

	# Connect to MySQL server
	db_connector = mysql.connector.connect(host="localhost", user="", password="")
	db_cursor = db_connector.cursor()

	# Fetch list of databases
	db_cursor.execute("SHOW DATABASES")

	# Check if IMPORT_TEST exists; if not, create it
	isDatabaseExists = False
	for db in db_cursor:
		if test_database == db:
			isDatabaseExists = True
	try:
		if not isDatabaseExists:
			db_cursor.execute(f"CREATE DATABASE {test_database}")
	except Exception as e:
		pass # Ignore exceptions for now
	db_cursor.execute(f"USE {test_database}")

	# Fetch list of tables
	db_cursor.execute("SHOW TABLES")

	# Check if table TICK_DATA_TEST exists; if not, create it
	isTableExists = False
	for db in db_cursor:
		if test_table == db:
			isTableExists = True
	try:
		if not isTableExists:
			db_cursor.execute(f"CREATE TABLE {test_table} (trade_id INT, price FLOAT, qty FLOAT, quoteQty FLOAT, time BIGINT(255), isBuyerMaker VARCHAR(255), isBestMatch VARCHAR(255))")
	except Exception as e:
		pass # Ignore exceptions for now

	# Search for Parquet and compressed CSV files
	parquet_files, zip_files = list_files_in_directory(directory_to_search)


	# Sort list of compressed csv files
	zip_files.sort()

	# Process CSV files
	process_csv_to_parquet(zip_files, db_connector, db_cursor)