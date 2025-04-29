# lstm_release.py
# Code development was assisted by an LLM (Qwen2.5-coder:32b). Check ai_disclaimer.pdf for prompts and responses.
# NOTE: MySQL database credentials have been removed for privacy/security reasons. 
# NOTE: Fill in these values before running this script.

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from datetime import datetime
import os
import joblib
import argparse
import pymysql
import sys

# File paths for training and testing data
TRAINING_FILE_PATH = 'training_data.parquet'
TESTING_FILE_PATH = 'testing_data.parquet'

# Directory paths for intermediate batch files
BATCH_DIR_PATH = 'batch_files/'
os.makedirs(BATCH_DIR_PATH, exist_ok=True)

# Output file path for predictions
PREDICTIONS_FILE_PATH = 'predictions.csv'

# File path for the MinMaxScaler
SCALER_FILE_PATH = 'scaler.pkl'

INDICES_FILE_PATH = 'test_indices.txt'

# Load test indices from file
def load_test_indices():
	with open(INDICES_FILE_PATH, 'r') as f:
		start_index = f.readline()
		end_index = f.readline()

	return int(start_index), int(end_index)


# Load the preprocessed data
def load_data(file_path):
	data = pd.read_parquet(file_path)
	
	# Check for NaN values
	if data.isnull().values.any():
		raise ValueError(f"Data in {file_path} contains NaN values.")
	
	return data

# Create sequences of data for LSTM using vectorized operations in batches and save them immediately to disk
def create_sequences_in_batches(data, seq_length=60, batch_size=100_000, file_prefix='train'):
	data_array = data[['price', 'volume', 'time', 'side']].values
	
	# Check for NaN values in the array
	if np.isnan(data_array).any():
		raise ValueError("Data array contains NaN values during sequence creation.")
	
	num_samples = len(data_array) - seq_length
	
	batch_counter = 0
	
	for start in range(0, num_samples, batch_size):
		end = min(start + batch_size, num_samples)
		X_batch = np.array([data_array[i:i + seq_length] for i in range(start, end)])
		y_batch = data_array[start + seq_length:end + seq_length, 0]  # Only the price column for target
		
		# Check for NaN values in batches
		if np.isnan(X_batch).any() or np.isnan(y_batch).any():
			raise ValueError(f"Batch {batch_counter} contains NaN values.")
		
		# Save the current batch to disk
		np.savez_compressed(f"{BATCH_DIR_PATH}/{file_prefix}_batch_0{batch_counter}.npz", X=X_batch, y=y_batch)
		
		# Increment batch counter
		batch_counter += 1

# Load batches from disk with a limit on the number of batches in RAM at a time
def load_batches(file_prefix, max_batches_in_memory=8):
	batch_files = sorted([f for f in os.listdir(BATCH_DIR_PATH) if f.startswith(file_prefix)])
	
	for i in range(0, len(batch_files), max_batches_in_memory):
		batch_chunk = batch_files[i:i + max_batches_in_memory]
		
		X_batches_chunk = []
		y_batches_chunk = []
		
		for file_name in batch_chunk:
			with np.load(f"{BATCH_DIR_PATH}/{file_name}") as data:
				X_batch = data['X']
				y_batch = data['y']
				
				# Check for NaN values in loaded batches
				if np.isnan(X_batch).any() or np.isnan(y_batch).any():
					raise ValueError(f"Loaded batch from {file_name} contains NaN values.")
				
				X_batches_chunk.append(X_batch)
				y_batches_chunk.append(y_batch)
		
		yield X_batches_chunk, y_batches_chunk

# Load the MinMaxScaler if it exists
def load_scaler(scaler_file_path):
	try:
		scaler = joblib.load(scaler_file_path)
		print("MinMaxScaler loaded successfully.")
		return scaler
	except FileNotFoundError:
		raise ValueError(f"Scaler file not found at {scaler_file_path}")
	except Exception as e:
		raise ValueError(f"Error loading scaler: {e}")
	
# Function to connect to the MySQL database
def get_db_connection(db_config):
	return pymysql.connect(**db_config)

# Main function to train and test the LSTM model
def main(table_prefix):

	# Database connection parameters
	DB_CONFIG = {
		'host': 'localhost',
		'user': '',
		'password': '',
		'database': 'PROJECT_4560'
	}
	
	# Connect to database
	connection = get_db_connection(DB_CONFIG)

	# Load data
	training_data = load_data(table_prefix + "_" + TRAINING_FILE_PATH)
	testing_data = load_data(table_prefix + "_" + TESTING_FILE_PATH)
	
	# Load or create MinMaxScaler
	if os.path.exists(SCALER_FILE_PATH):
		scaler = load_scaler(SCALER_FILE_PATH)
	else:
		raise ValueError(f"Scaler file not found at {SCALER_FILE_PATH}")
	
	# Normalize data (ensure consistency with preprocessing)
	training_scaled = scaler.transform(training_data[['price', 'volume', 'time']])
	testing_scaled = scaler.transform(testing_data[['price', 'volume', 'time']])
	
	# Check for NaN values after scaling
	if np.isnan(training_scaled).any() or np.isnan(testing_scaled).any():
		raise ValueError("Scaled data contains NaN values.")
	
	# Create sequences in batches and save them immediately to disk
	seq_length = 60
	batch_size = 100_000
	
	create_sequences_in_batches(training_data, seq_length, batch_size, file_prefix='train')
	create_sequences_in_batches(testing_data, seq_length, batch_size, file_prefix='test')
	
	# Build the LSTM model
	model = Sequential()
	model.add(LSTM(units=50, return_sequences=True, input_shape=(seq_length, 4)))  # Corrected input shape to (60, 4)
	model.add(Dropout(0.2))
	model.add(LSTM(units=50, return_sequences=False))
	model.add(Dropout(0.2))
	model.add(Dense(units=1))
	
	# Compile the model
	model.compile(optimizer='adam', loss='mean_squared_error')
	
	# Train the model in batches
	start_time = datetime.now()
	for X_train_batches, y_train_batches in load_batches('train'):
		for i, (X_train_batch, y_train_batch) in enumerate(zip(X_train_batches, y_train_batches)):
			print(f"Training batch {i + 1}/{len(X_train_batches)}")
			model.fit(X_train_batch, y_train_batch, epochs=1, batch_size=32, validation_split=0.2)
	end_time = datetime.now()
	
	print(f"Model trained in {end_time - start_time}")
	
	# Evaluate the model on test data
	y_pred_all = []
	y_test_all = []
	side_test_all = []
	time_test_all = []  # Added to store actual timestamps
	
	for X_test_batches, y_test_batches in load_batches('test'):
		for i, (X_test_batch, y_test_batch) in enumerate(zip(X_test_batches, y_test_batches)):
			print(f"Evaluating batch {i + 1}/{len(X_test_batches)}")
			y_pred = model.predict(X_test_batch)
			y_pred_all.extend(y_pred.flatten())
			y_test_all.extend(y_test_batch)
			
			# Extract side and time values from the testing data
			start_idx = seq_length - 1 + i * batch_size
			end_idx = min(start_idx + len(y_test_batch), len(testing_data) - 1)
			print(f"Start index: {start_idx}, End index: {end_idx}")
			side_values = testing_data['side'].iloc[start_idx:end_idx].values
			time_values = testing_data['time'].iloc[start_idx:end_idx].values
			
			side_test_all.extend(side_values)
			time_test_all.extend(time_values)
	
	# Convert lists to numpy arrays
	y_pred_inv = np.array(y_pred_all).reshape(-1, 1)
	y_test_inv = np.array(y_test_all).reshape(-1, 1)
	side_test_inv = np.array(side_test_all).reshape(-1, 1)
	#time_test_inv = np.array(time_test_all).reshape(-1, 1)  # Convert time to numpy array
	
	# Create a temporary DataFrame for inverse transformation
	temp_test = pd.DataFrame(scaler.inverse_transform(testing_scaled), columns=['price', 'volume', 'time'])
	
	# Adjust the indices to match the sequences
	#print(f"Length of y_pred_all: {len(y_pred_all)}")
	#print(f"Length of testing_data: {len(testing_data)}")
	#print(f"Length of temp_test: {len(temp_test)}")
	
	y_pred_inv_full = np.zeros((len(y_pred_all), 3))
	y_pred_inv_full[:, 0] = y_pred_inv.flatten()
	
	start_idx = seq_length - 1
	end_idx = start_idx + len(y_pred_all)
	#print(f"Adjusted start index: {start_idx}, Adjusted end index: {end_idx}")
	
	y_pred_inv_full[:, 1:3] = temp_test.iloc[start_idx:end_idx][['volume', 'time']].values
	
	y_test_inv_full = np.zeros((len(y_test_all), 3))
	y_test_inv_full[:, 0] = y_test_inv.flatten()
	y_test_inv_full[:, 1:3] = temp_test.iloc[start_idx:end_idx][['volume', 'time']].values

	# Check for NaN values before inverse transformation
	if np.isnan(y_pred_inv_full).any() or np.isnan(y_test_inv_full).any():
		raise ValueError("Data contains NaN values before inverse transformation.")
	
	# Inverse transform the entire sequences (only price, volume, and time)
	y_pred_inv_full[:, :3] = scaler.inverse_transform(y_pred_inv_full[:, :3])
	y_test_inv_full[:, :3] = scaler.inverse_transform(y_test_inv_full[:, :3])
	
	# Check for NaN values after inverse transformation
	if np.isnan(y_pred_inv_full).any() or np.isnan(y_test_inv_full).any():
		raise ValueError("Data contains NaN values after inverse transformation.")
	
	# Calculate performance metrics
	mse = mean_squared_error(y_test_inv_full[:, 0], y_pred_inv_full[:, 0])
	mae = mean_absolute_error(y_test_inv_full[:, 0], y_pred_inv_full[:, 0])
	
	print(f"Mean Squared Error (MSE): {mse}")
	print(f"Mean Absolute Error (MAE): {mae}")

	# Load start/end test indices
	start_index, end_index = load_test_indices()

	# Get time column from database
	start_index += 61
	source_table = table_prefix + "_TICK_DATA"
	with connection.cursor() as cursor:
		time_query = f"SELECT time FROM {source_table} WHERE trade_id BETWEEN {start_index} AND {end_index}"
		cursor.execute(time_query)
		connection.commit()

		result_time = cursor.fetchall()
		time_column = [row[0] for row in result_time]

	#print(f"Length of y_pred_inv_full[:, 0]: {len(y_pred_inv_full[:, 0])}")
	#print(f"Length of y_test_inv_full[:, 1]: {len(y_test_inv_full[:, 1])}")
	#print(f"Length of time_column: {len(time_column)}")
	#print(f"Length of side_test_inv.flatten(): {len(side_test_inv.flatten())}")
	
	# Save predictions to a dataframe
	results_df = pd.DataFrame({
		#'actual_price': y_test_inv_full[:, 0],
		'predicted_price': y_pred_inv_full[:, 0],
		'volume': y_test_inv_full[:, 1],
		'time': time_column,  # Use actual timestamps
		'side': side_test_inv.astype(int).flatten()  # Convert side to int
	})

	# Save dataframe to the database
	predict_table = table_prefix + "_TICK_DATA_predict"
	with connection.cursor() as cursor:
		try:
			results_df = results_df.replace(np.nan, None)
			results_val = list(results_df.itertuples(index=False, name=None))

			drop_query = f"DROP TABLE IF EXISTS {predict_table}"
			cursor.execute(drop_query)
			connection.commit()

			results_query = f"CREATE TABLE IF NOT EXISTS {predict_table} (trade_id INT NOT NULL AUTO_INCREMENT, price FLOAT, volume FLOAT, time DOUBLE PRECISION(19,8), side INT, PRIMARY KEY (trade_id))"
			cursor.execute(results_query)
			connection.commit()

			results_query = f"ALTER TABLE {predict_table} AUTO_INCREMENT={start_index}"
			cursor.execute(results_query)
			connection.commit()

			results_query = f"INSERT INTO {predict_table} (price, volume, time, side) VALUES (%s, %s, %s, %s)"
			cursor.executemany(results_query, results_val)
			connection.commit()
		except Exception as e:
			print(f"An error occurred inserting data into the database: {e}")
			sys.exit()
	
	# DEBUG: Save predictions to a CSV file
	results_df.to_csv(table_prefix + "_" + PREDICTIONS_FILE_PATH, index=False)
	print(f"Predictions saved to {table_prefix + "_" + PREDICTIONS_FILE_PATH}")
	
	# Optional: Save the model
	model.save('lstm_model.keras')
	
	# Cleanup batch files
	cleanup_batch_files()

# Function to clean up batch files
def cleanup_batch_files():
	for file_name in os.listdir(BATCH_DIR_PATH):
		if file_name.endswith('.npz'):
			file_path = os.path.join(BATCH_DIR_PATH, file_name)
			try:
				os.remove(file_path)
				print(f"Deleted batch file: {file_path}")
			except Exception as e:
				print(f"Error deleting batch file {file_path}: {e}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Train LSTM model on preprocessed data.")
	parser.add_argument('--table-prefix', type=str, required=True, help='Prefix of the table name (e.g., ETHUSDC)')
	
	args = parser.parse_args()

	start_time = datetime.now()
	main(args.table_prefix)
	end_time = datetime.now()
	
	print(f"Total execution time: {end_time - start_time}")
