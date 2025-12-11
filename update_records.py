import csv
import sqlite3
import argparse
import logging

# --- Setup Logging ---
log_file = 'update.log'
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

def update_records(db_path, corrected_csv_path, project_id):
    """
    Updates records in the database based on a corrected CSV file.
    """
    logging.info("--- Starting Database Record Update Process ---")
    table_name = f"pid_{project_id}"

    # --- 1. Read the corrected data ---
    logging.info(f"Reading corrected data from: {corrected_csv_path}")
    try:
        with open(corrected_csv_path, 'r') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ['id', 'record']:
                logging.error(f"FATAL: Invalid header in {corrected_csv_path}. Expected ['id', 'record'].")
                return
            corrected_data = list(reader)
        logging.info(f"Successfully loaded {len(corrected_data)} corrected records.")
    except FileNotFoundError:
        logging.error(f"FATAL: Corrected data file not found at {corrected_csv_path}")
        return
    except Exception as e:
        logging.error(f"FATAL: Failed to read corrected data file: {e}")
        return

    # --- 2. Connect to the database and update records ---
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        logging.info(f"Successfully connected to database: {db_path}")

        # Verify table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cur.fetchone():
            logging.error(f"FATAL: Table '{table_name}' does not exist in the database.")
            conn.close()
            return
        
        logging.info(f"--- Starting updates on table '{table_name}' ---")
        for row in corrected_data:
            record_id = row['id']
            new_record = row['record']
            
            logging.info(f"Updating ID '{record_id}' with new record '{new_record}'")
            
            cur.execute(f"UPDATE {table_name} SET record = ? WHERE id = ?", (new_record, record_id))
            
            if cur.rowcount == 0:
                logging.warning(f"  - ID '{record_id}' not found in the database. No update performed.")
            else:
                logging.info(f"  - Successfully updated ID '{record_id}'.")

        conn.commit()
        logging.info("--- Database updates committed successfully ---")

    except sqlite3.Error as e:
        logging.error(f"FATAL: Database error: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
            logging.info("Database transaction rolled back.")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logging.info("Database connection closed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Update REDCap Booster records in the database from a CSV file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'database_path',
        help="Path to the SQLite database file (e.g., 'id_gen.db')."
    )
    parser.add_argument(
        'corrected_csv',
        help="Path to the CSV file containing the corrected data.\nExpected header: id,record"
    )
    parser.add_argument(
        'project_id',
        help="The project ID for the database table (e.g., '16894')."
    )

    args = parser.parse_args()

    update_records(args.database_path, args.corrected_csv, args.project_id)
