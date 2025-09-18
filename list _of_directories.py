import os
import csv

def list_top_level_directories(base_path, output_csv='output/top_level_dirs.csv'):
    base_path = os.path.abspath(base_path)

    # Get only top-level directories
    top_dirs = [
        name for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]

    # Save CSV to script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_csv)

    # Write CSV
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Directory Name'])
        for dir_name in top_dirs:
            writer.writerow([dir_name])

    print(f"✅ Top-level directories written to: {output_path}")

# Example usage
if __name__ == "__main__":
    list_top_level_directories('D:/')  # Change this to your desired path
