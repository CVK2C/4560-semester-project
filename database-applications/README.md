## Data Importer Instructions

1. Set up Python virtual environment
2. Install dependencies: `pip install pandas pyarrow numpy mysql-connector-python`
3. Run script: `python3 data-importer-release --directory /path/to/files`

## Data Preprocessing

1. Set up or reuse previous Python virtual environment
2. Install dependencies: `pip install pymysql pandas scikit-learn`
3. Run script: `python3 preprocess-release.py --table-prefix TABLE_PREFIX`

## LSTM Model

1. Set up or reuse previous Python virtual environment
2. Install dependencies: `pip install scikit-learn tensorflow[and-cuda] joblib`
3. Run script: `python3 lstm-release.py --table-prefix TABLE_PREFIX`

Note: A supported Nvidia GPU and the CUDA Toolkit are required to run this script
