import os
import shutil
from langdetect import detect
from iso639 import languages
import pandas as pd
import re
import logging


# Configure logging
logger = logging.getLogger()  # Get the root logger
logger.setLevel(logging.INFO)

# File Handler - logs to a file
file_handler = logging.FileHandler('edit_srt_files.log')
file_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Stream Handler - logs to the console
stream_handler = logging.StreamHandler()
stream_format = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)


def iterate_directories(path):
    '''
    This function iterates through all directories in the root.
    '''
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            yield os.path.join(root, dir)


def get_iso639_1_code(language_name):
    '''
    This function gets the ISO-639-1 code for the language.
    '''
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
        logging.error(f"Error getting ISO-639-1 code for {language_name}: {e}")
        return language_name

    
def extract_language_code(filename):
    # Regular expression to match two or three letter language codes
    pattern = r'\.([a-zA-Z]{2,3})\.srt$'
    match = re.search(pattern, filename)
    if match:
        return match.group(1).replace('.str','').lower()
    return None


def extract_language(root, file):
    '''
    This function extracts the language from the file name.
    If the language is not in the file name, it tries to detect the language from the file content.
    Only process .srt files for language detection.
    '''
    language = None
    file_name = os.path.basename(file)
    logging.info(f"Extracting langauge, base file name is: {file_name}")
    logging.info(f"Root is: {root}")

    

    if file_name.endswith('.srt'):  # Only process .srt files
        # Attempt to detect from content
        file_path = os.path.join(root, file)
        if os.path.exists(file_path):  # Check if the file exists
            logging.info(f"Attempting to extracting language from file: {file_path}")
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                srt_file_content = f.read()
                language = detect(srt_file_content)
                language = language.lower()
        else:
            logging.error(f"File not found: {file_path}, attempting to extract language from file name.")
            language_code = extract_language_code(file)
            logging.info(f"Language code is: {language_code}")
            if language_code is not None:
                return 'eng'
            return language_code
    elif '_' in file_name:
        language = file_name.split('_')[-1].split('.')[0].lower()
    elif language is None:
        language_code = extract_language_code(file)
        if language_code is not None:
            return language_code
        logging.error(f"Could not extract language for {file}. Defaulting to eng (English).")
        return 'eng'
    # Get ISO-639-1 code
    lang = get_iso639_1_code(language)
    if lang is None and (language is not None or lang == 'und' or lang == "" or lang == " "):
        logging.error(f"Could not find ISO-639-1 code for {language}. Defaulting to eng (English).")
        return language
    logging.info(f"Language: {language}. ISO-639-1 code: {lang}")
    return lang


def edit_srt_files(root_folder):
    '''
    This function moves .srt files from subfolders to the root folder of the movie.
    It also renames the .srt files to match the movie name and language.
    '''
    
    movies_without_srt_files = None
    num=1 # used to add a number to the end of the file name if the file name already exists
    for root, dirs, files in os.walk(root_folder):
        print(f"Root is: {root}")
        # Check if there are any files with .srt, .idx, or .sub extensions
        if any(file.endswith(('.srt', '.idx', '.sub')) for file in os.listdir(root)) and 'Subs' not in dirs:
            # filtered for-loop that only iterates through .srt, .idx, and .sub files
            for file in files:
                if file.endswith(('.srt', '.idx', '.sub')):
                    # extract ext from sub_file
                    sub_file_ext = os.path.splitext(file)[1]
                    logging.info(f"Reviewing moving root folder file: {file} from: {root}")
                    movie_folder = os.path.basename(root)
                    logging.info(f"Movie folder is: {movie_folder}")
                    movie_name = os.path.splitext(movie_folder)[0]
                    logging.info(f"Movie name is: {movie_name}")
                    language = extract_language(root, file)
                    logging.info(f"Language is: {language}")
                    new_file_name = f"{movie_name}.{language}{sub_file_ext}"
                    new_file_path = os.path.join(root, new_file_name)
                    logging.info(f"New file path is: {new_file_path}")
                    # new file name not same as old file name and new file path does not exist
                    if new_file_name != file and not os.path.exists(new_file_path):
                        logging.info(f"Moving: {file} aka {new_file_name} to: {root}\n")
                        shutil.move(os.path.join(root, file), new_file_path)
                    # new file name not same as old file name and new file path with file does exist and new file name does match the regex pattern
                    elif new_file_name != file and os.path.exists(new_file_path) and new_file_name == re.sub(r'\.\d+\.', '.', file):
                        logging.info(f"Filepath already exists for {file} renamed to {new_file_name}, adding number to file name.")
                        num += 1
                        new_file_name = f"{movie_name}.{num}.{language}{sub_file_ext}"
                        new_file_path = os.path.join(root, new_file_name)
                        shutil.move(os.path.join(root, file), new_file_path)
                        logging.info(f"Updated file name is: {new_file_name} in path {new_file_path}\n")
                    # new file name same as old file name and new file path with new file name does not exist
                    elif new_file_name == file or new_file_name == re.sub(r'\.\d+\.', '.', file):
                        logging.info(f"File name already matches for {file}, skipping metadata update.\n")
                        continue
        
        elif 'Subs' in dirs:
            # Check if there are any files with .srt, .idx, or .sub extensions
            subs_folder = os.path.join(root, 'Subs')
            num=1 # used to add a number to the end of the file name if the file name already exists
            for sub_root, sub_dirs, sub_files in os.walk(subs_folder):
                for sub_file in sub_files:
                    if sub_file.endswith('.srt') or sub_file.endswith('.idx') or sub_file.endswith('.sub'):
                        # extract ext from sub_file
                        logging.info(f"Reviewing Subs folder: {sub_file} from: {sub_root}")
                        sub_file_ext = os.path.splitext(sub_file)[1]
                        logging.info(f"Moving: {sub_file} to: {root}")
                        movie_folder = os.path.basename(root)
                        logging.info(f"Movie folder is: {movie_folder}")
                        movie_name = os.path.splitext(movie_folder)[0]
                        logging.info(f"Movie name is: {movie_name}")
                        language = extract_language(sub_root, sub_file)
                        logging.info(f"Language is: {language}")
                        new_file_name = f"{movie_name}.{language}{sub_file_ext}"
                        logging.info(f"New file name is: {new_file_name}")
                        new_file_path = os.path.join(root, new_file_name)
                        logging.info(f"New file path is: {new_file_path}")
                        # new file name not same as old file name and new file path does not exist
                        if new_file_name != sub_file and not os.path.exists(new_file_path):
                            logging.info(f"Moving: {new_file_name} to: {root}\n")
                            shutil.move(os.path.join(sub_root, sub_file), new_file_path)
                        # new file name not same as old file name and new file path does exist and new file name does not match the regex pattern
                        elif new_file_name != sub_file and os.path.exists(new_file_path): # and new_file_name == re.sub(r'\.\d+\.', '.', sub_file):
                            logging.info(f"Filepath already exists for {sub_file} renamed to {new_file_name}, adding number to file name.")
                            num += 1
                            new_file_name = f"{movie_name}.{num}.{language}{sub_file_ext}"
                            new_file_path = os.path.join(root, new_file_name)
                            shutil.move(os.path.join(sub_root, sub_file), new_file_path)
                            logging.info(f"Updated file name is: {new_file_name} in path {new_file_path}\n")
                        # new file name same as old file name and new file path with new file name does not exist
                        elif new_file_name == sub_file and not os.path.exists(new_file_path):
                            logging.info(f"File name already matches for {sub_file}, But is in sub folder, moving to root folder.\n")
                            shutil.move(os.path.join(sub_root, sub_file), new_file_path)
                        # new file name same as old file name with regex, still need to move to root folder
                        elif new_file_name == re.sub(r'\.\d+\.', '.', sub_file):
                            logging.info(f"Rare accurance, New file name {new_file_name} matches with old {sub_file}. Adding number to file name.")
                            num += 1
                            new_file_name = f"{movie_name}.{num}.{language}{sub_file_ext}"
                            new_file_path = os.path.join(root, new_file_name)
                            shutil.move(os.path.join(sub_root, sub_file), new_file_path)
                            logging.info(f"Updated file name is: {new_file_name} in path {new_file_path}\n")
                        else:
                            logging.info(f"File name: {new_file_name} already matches for {sub_file}, skipping metadata update.\n")
                            continue
                
                shutil.rmtree(subs_folder)
        
        else:
            logging.info(f"No SRT files found or no SRT files to edit, for {root}.")
            movie_folder = os.path.basename(root)
            movie_name = os.path.splitext(movie_folder)[0]
            movies_without_srt_files = movie_name
            logging.info(f"Movie name is: {movie_name}, appending to list of movies without SRT files.\n")
            

    return movies_without_srt_files

if __name__ == "__main__":
    
    test_path = "E:\Movie_edit_testing\Movies"
    nas_path = '//10.0.0.148/Media/Movies'  
    local_path = 'E:\Videos'  
    
    df = pd.DataFrame()
    logging.info(f"Starting program for folder: {local_path}")
    for directory in iterate_directories(local_path):
        movie_w_no_srt = edit_srt_files(directory)
        if movie_w_no_srt is not None:
            df = df.append({'movies_with_no_srt_file': movie_w_no_srt}, ignore_index=True)
            
    df.to_csv('movies_without_srt_files.csv', index=False)
    logging.info("Finished editing SRT files.")
    