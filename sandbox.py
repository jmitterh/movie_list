import re

# def clean_filename(filename):
#     # Regular expression pattern to match '{num}.'
#     pattern = r'\.\d+\.'

#     # Replace the matched pattern with an empty string
#     cleaned_filename = re.sub(pattern, '.', filename)

#     return cleaned_filename

# # Example usage
# file = "some name (2010) 1080p.123.en.srt"
# cleaned_filename = clean_filename(file)
# print(cleaned_filename)



# print(re.sub(r'\.\d+\.', '.', file))


'''Function to find None.srt files in a log file and save to CSV'''
import pandas as pd
import re

def find_none_srt_filenames(log_file):
    pattern = r"New file name is: (.+\.None\.srt)"
    file_names = []

    # Open and read the log file
    with open(log_file, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                print("match.group(1):", match.group(1))
                file_names.append(match.group(1))

    # Create DataFrame and remove duplicates
    df = pd.DataFrame(file_names, columns=['File Names'])
    df = df.drop_duplicates()

    # Save to CSV
    df.to_csv('None_srt_file_names.csv', index=False)

    print("CSV file saved as 'None_srt_file_names.csv'")

# Example usage
# log_file = 'edit_srt_files.log'
# find_none_srt_filenames(log_file)


''' Testing the get_iso639_1_code() function '''
from iso639 import languages
def get_iso639_1_code(language_name):
    
    char_count = len(language_name)
    try:
        if char_count == 2:
            lang = languages.get(part1=language_name.lower())
            return lang.part1  # Use ISO-639-1 codes
        elif char_count == 3:
            lang = languages.get(part2b=language_name.lower())
            return lang.part1  # Use ISO-639-1 codes
        elif char_count > 3 and char_count < 8:
            lang = languages.get(name=language_name.title())
            return lang.part1
        else:
            return None
    except Exception as e:
        print(f"Error getting ISO-639-1 code for {language_name}: {e}")
        return language_name
    
print(get_iso639_1_code('spa'))