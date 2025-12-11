import csv
import logging
import argparse

# --- Setup Logging ---
log_file = 'correction.log'
# Clear the log file before running
with open(log_file, 'w'):
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def correct_ids(source_csv_path, corrections_csv_path, output_csv_path):
    """
    Corrects ID assignments in a source CSV file based on a 'daisy-chain'
    correction mapping.
    """
    logging.info("--- Starting ID Correction Process (v2: Daisy-Chain) ---")

    # --- 1. Read and process corrections ---
    logging.info(f"Reading corrections from: {corrections_csv_path}")
    corrections = {}
    try:
        with open(corrections_csv_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            if header != ['current_id', 'corrected_id']:
                logging.error(f"FATAL: Invalid header in {corrections_csv_path}. Expected ['current_id', 'corrected_id'].")
                return

            for i, row in enumerate(reader, 2):
                if len(row) != 2:
                    logging.warning(f"Skipping malformed row {i} in {corrections_csv_path}: {row}")
                    continue
                current_id, corrected_id = row
                corrections[current_id] = corrected_id
        logging.info(f"Successfully loaded {len(corrections)} correction rules.")
    except FileNotFoundError:
        logging.error(f"FATAL: Corrections file not found at {corrections_csv_path}")
        return
    except Exception as e:
        logging.error(f"FATAL: Failed to read corrections file: {e}")
        return

    # --- 2. Read the source data ---
    logging.info(f"Reading source data from: {source_csv_path}")
    try:
        with open(source_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ['id', 'record']:
                 logging.error(f"FATAL: Invalid header in {source_csv_path}. Expected ['id', 'record'].")
                 return
            # Create a deep copy for the final output
            original_data = list(reader)
            corrected_data = [row.copy() for row in original_data]
            
        original_data_by_id = {row['id']: row for row in original_data}
        corrected_data_by_id = {row['id']: row for row in corrected_data}
        logging.info(f"Successfully loaded {len(original_data)} records from {source_csv_path}.")
    except FileNotFoundError:
        logging.error(f"FATAL: Source data file not found at {source_csv_path}")
        return
    except Exception as e:
        logging.error(f"FATAL: Failed to read source data file: {e}")
        return

    # --- 3. Perform the assignments (Daisy-Chain) ---
    logging.info("--- Starting Record Assignments ---")
    for current_id, corrected_id in corrections.items():
        if current_id not in original_data_by_id:
            logging.warning(f"Skipping assignment: `current_id` '{current_id}' not found in {source_csv_path}")
            continue
        if corrected_id not in corrected_data_by_id:
            logging.warning(f"Skipping assignment: `corrected_id` '{corrected_id}' not found in {source_csv_path}")
            continue

        # Get the record from the *original* data
        record_to_move = original_data_by_id[current_id]['record']

        logging.info(f"Assigning record from '{current_id}' to '{corrected_id}'")
        logging.info(f"  - Moving record '{record_to_move}' -> to ID '{corrected_id}'")
        
        # Assign it to the *corrected* data
        corrected_data_by_id[corrected_id]['record'] = record_to_move
        
    logging.info("--- Record Assignments Complete ---")

    # --- 4. Validate the assignments ---
    logging.info("--- Starting Validation ---")
    validation_passed = True
    for current_id, corrected_id in corrections.items():
        if current_id not in original_data_by_id:
            logging.warning(f"Skipping validation for missing `current_id`: {current_id}")
            continue
        if corrected_id not in corrected_data_by_id:
            logging.warning(f"Skipping validation for missing `corrected_id`: {corrected_id}")
            continue

        original_record = original_data_by_id[current_id]['record']
        new_record_on_corrected_id = corrected_data_by_id[corrected_id]['record']

        if new_record_on_corrected_id == original_record:
            logging.info(f"  [PASS] ID '{corrected_id}' correctly received record '{original_record}' from '{current_id}'.")
        else:
            logging.error(f"  [FAIL] Validation failed for assignment: '{current_id}' -> '{corrected_id}'")
            logging.error(f"    - Expected ID '{corrected_id}' to have record '{original_record}', but found '{new_record_on_corrected_id}'.")
            validation_passed = False

    if not validation_passed:
        logging.error("--- FATAL: Validation Failed. Corrected file will NOT be written. ---")
        return
    logging.info("--- Validation Successful ---")

    # --- 5. Write the corrected file ---
    logging.info(f"Writing corrected data to: {output_csv_path}")
    try:
        with open(output_csv_path, 'w', newline='') as f:
            fieldnames = ['id', 'record']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(corrected_data_by_id.values())
        logging.info(f"--- Process Complete. '{output_csv_path}' created. ---")
    except Exception as e:
        logging.error(f"FATAL: Failed to write corrected file: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Correct REDCap Booster ID assignments using a 'daisy-chain' mapping.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'source_csv',
        help="Path to the source CSV file (e.g., 'out.csv').\nExpected header: id,record"
    )
    parser.add_argument(
        'corrections_csv',
        help="Path to the CSV file with correction mappings.\nExpected header: current_id,corrected_id"
    )
    parser.add_argument(
        'output_csv',
        help="Path to write the new, corrected CSV file to (e.g., 'corrected_ids.csv')."
    )

    args = parser.parse_args()

    correct_ids(args.source_csv, args.corrections_csv, args.output_csv)
