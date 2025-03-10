#!/bin/bash

# Load the .env file if it exists
if [ -f $SCRIPT_DIR/.env ]; then
    source $SCRIPT_DIR/.env
else
    echo "Error: .env file not found."
    exit 1
fi

# Run main_api_extract.py
echo "Running main_api_extract.py..."
python3 $SCRIPT_DIR/main_api_extract.py
if [ $? -ne 0 ]; then
    echo "Error running main_api_extract.py"
    exit 1
fi

# Run main_transform.py
echo "Running main_transform.py..."
python3 $SCRIPT_DIR/main_transform.py
if [ $? -ne 0 ]; then
    echo "Error running main_transform.py"
    exit 1
fi

# Run load_data.py
echo "Running load_data.py..."
python3 $SCRIPT_DIR/load_data.py
if [ $? -ne 0 ]; then
    echo "Error running load_data.py"
    exit 1
fi

echo "ETL process completed successfully."