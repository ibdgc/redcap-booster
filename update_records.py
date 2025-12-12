import argparse
import csv
import logging
import sqlite3
import uuid

# --- Setup Logging ---
log_file = "update_v6.log"
with open(log_file, "w"):
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)


def update_ids_transactional(db_path, corrections_csv_path, project_id):
    """
    Updates IDs in the database using a transactional two-phase update
    to handle UNIQUE constraints on the ID column.
    """
    logging.info("--- Starting Database ID Update Process (v6: Corrected Two-Phase) ---")
    table_name = f"pid_{project_id}"

    # --- 1. Read the correction data ---
    logging.info(f"Reading correction data from: {corrections_csv_path}")
    try:
        with open(corrections_csv_path, "r") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ["current_id", "corrected_id"]:
                logging.error(
                    f"FATAL: Invalid header in {corrections_csv_path}. Expected ['current_id', 'corrected_id']."
                )
                return
            corrections = list(reader)
        logging.info(f"Successfully loaded {len(corrections)} correction rules.")
    except FileNotFoundError:
        logging.error(f"FATAL: Corrections file not found at {corrections_csv_path}")
        return
    except Exception as e:
        logging.error(f"FATAL: Failed to read corrections file: {e}")
        return

    conn = None
    try:
        # --- 2. Connect to DB and start a transaction ---
        conn = sqlite3.connect(db_path)
        conn.isolation_level = None
        cur = conn.cursor()
        cur.execute("BEGIN")
        logging.info(
            f"Successfully connected to database '{db_path}' and started transaction."
        )

        # Verify table exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        if not cur.fetchone():
            logging.error(
                f"FATAL: Table '{table_name}' does not exist in the database."
            )
            cur.execute("ROLLBACK")
            conn.close()
            return
            
        # --- 3. Create a temporary table for the updates ---
        temp_table_name = f"temp_updates_{uuid.uuid4().hex}"
        logging.info(f"--- Creating temporary table '{temp_table_name}' ---")
        cur.execute(f"CREATE TABLE {temp_table_name} (current_id TEXT, corrected_id TEXT)")
        cur.executemany(f"INSERT INTO {temp_table_name} VALUES (?, ?)", [(c['current_id'], c['corrected_id']) for c in corrections])


        # --- 4. Phase 1: Update IDs to temporary values ---
        logging.info(f"--- Phase 1: Updating IDs in '{table_name}' to temporary values ---")
        
        # We generate a temporary ID that includes the original ID to avoid collisions and keep track
        cur.execute(f"""
            UPDATE {table_name}
            SET id = 'temp_id_swap_' || id
            WHERE id IN (SELECT current_id FROM {temp_table_name})
        """
        )
        
        logging.info(f"  - Updated {cur.rowcount} records to temporary IDs.")
        logging.info("--- Phase 1 Complete ---")

        # --- 5. Phase 2: Update from temporary IDs to final 'corrected_id's ---
        logging.info(f"--- Phase 2: Updating IDs to their final values ---")
        
        # This join ensures that we are updating the correct record with the correct new ID
        cur.execute(f"""
            UPDATE {table_name}
            SET id = (
                SELECT t.corrected_id
                FROM {temp_table_name} t
                WHERE {table_name}.id = 'temp_id_swap_' || t.current_id
            )
            WHERE EXISTS (
                SELECT 1
                FROM {temp_table_name} t
                WHERE {table_name}.id = 'temp_id_swap_' || t.current_id
            )
        """
        )
        
        logging.info(f"  - Updated {cur.rowcount} records to their final IDs.")
        logging.info("--- Phase 2 Complete ---")

        # --- 6. Clean up temporary table ---
        logging.info(f"--- Dropping temporary table '{temp_table_name}' ---")
        cur.execute(f"DROP TABLE {temp_table_name}")

        # --- 7. Commit the transaction ---
        cur.execute("COMMIT")
        logging.info("--- Database transaction committed successfully ---")

    except Exception as e:
        logging.error(f"FATAL: An error occurred: {e}", exc_info=True)
        if conn:
            logging.info("Attempting to roll back database transaction.")
            cur.execute("ROLLBACK")
            logging.info("Database transaction rolled back.")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update REDCap Booster IDs in the database using a transactional two-phase update.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "database_path", help="Path to the SQLite database file (e.g., 'id_gen_original.db')."
    )
    parser.add_argument(
        "corrections_csv",
        help="Path to the CSV file containing the ID correction mappings.\nExpected header: current_id,corrected_id",
    )
    parser.add_argument(
        "project_id", help="The project ID for the database table (e.g., '16894')."
    )

    args = parser.parse_args()

    update_ids_transactional(
        args.database_path, args.corrections_csv, args.project_id
    )
