import os
import pandas as pd
import logging

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataLoader")

REQUIRED_COLUMNS = {
    "products.csv": {"name", "category", "price", "brand", "rating", "description"},
    "faqs.csv": {"question", "answer"}
}

def load_all_data(data_dir="data"):
    """
    Scans the given data directory for CSV and JSON files, loads them,
    and validates files with known schemas.
    
    Returns:
        dict: A dictionary mapping filename to pandas DataFrame.
        dict: A dictionary of validation warning messages.
    """
    dataframes = {}
    warnings = {}
    
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory '{data_dir}' does not exist.")
        return dataframes, warnings

    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        
        # Only process files
        if not os.path.isfile(file_path):
            continue
            
        df = None
        if file.endswith(".csv"):
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                logger.error(f"Error reading CSV file '{file}': {e}")
                warnings[file] = f"Error reading file: {e}"
        elif file.endswith(".json"):
            try:
                df = pd.read_json(file_path)
            except Exception as e:
                logger.error(f"Error reading JSON file '{file}': {e}")
                warnings[file] = f"Error reading file: {e}"
                
        if df is not None:
            # Validate columns if we have a known schema requirements for this filename
            if file in REQUIRED_COLUMNS:
                expected_cols = REQUIRED_COLUMNS[file]
                actual_cols = set(df.columns)
                missing_cols = expected_cols - actual_cols
                
                if missing_cols:
                    warn_msg = f"Missing required columns: {', '.join(missing_cols)}"
                    logger.warning(f"Validation warning for '{file}': {warn_msg}")
                    warnings[file] = warn_msg
                    # Skip files with invalid headers as requested in Section 7
                    continue
            
            dataframes[file] = df
            logger.info(f"Successfully loaded '{file}' with {len(df)} rows.")
            
    return dataframes, warnings
