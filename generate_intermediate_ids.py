import csv
import random
import string
import argparse

def generate_intermediate_ids(input_file, output_file):
    """
    Reads a corrections.csv file and generates a new CSV file with an added
    'intermediate_id' column.
    """
    print(f"--- Generating intermediate IDs from '{input_file}' ---")

    try:
        with open(input_file, 'r') as f_in, open(output_file, 'w', newline='') as f_out:
            reader = csv.DictReader(f_in)
            if reader.fieldnames != ['current_id', 'corrected_id']:
                print(f"FATAL: Invalid header in {input_file}. Expected ['current_id', 'corrected_id'].")
                return
            
            fieldnames = reader.fieldnames + ['intermediate_id']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                id_length = len(row['current_id'])
                intermediate_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=id_length))
                row['intermediate_id'] = intermediate_id
                writer.writerow(row)

        print(f"--- Successfully created '{output_file}' ---")
    except FileNotFoundError:
        print(f"FATAL: Input file not found at {input_file}")
    except Exception as e:
        print(f"FATAL: An error occurred: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Generate an intermediate corrections file with unique 'nonsense' IDs."
    )
    parser.add_argument(
        'input_csv',
        help="Path to the source corrections CSV file (e.g., 'corrections.csv')."
    )
    parser.add_argument(
        'output_csv',
        help="Path to write the new intermediate CSV file to (e.g., 'corrections_intermediate.csv')."
    )
    args = parser.parse_args()

    generate_intermediate_ids(args.input_csv, args.output_csv)
