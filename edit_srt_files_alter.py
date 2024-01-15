import os
import shutil
from langdetect import detect
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)
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


def extract_language(file_path):
    '''
    This function extracts the language from the file name.
    If the language is not in the file name, it tries to detect the language from the file content.
    '''
    # Attempt to extract language from the filename
    language = None
    file_name = os.path.basename(file_path)
    if '_' in file_name:
        language = file_name.split('_')[-1].split('.')[0].lower()
        logger.info(f"Language extracted from file name: {language}")
    else:
        # If not found, attempt to detect from content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                language = detect(content)
                logger.info(f"Language detected from content: {language}")
        except Exception as e:
            logger.error(f"Error detecting language for {file_name}: {e}")
            return None
    return language

def move_subtitle_files_to_root(movie_dir, subtitle_files):
    '''
    This function moves subtitle files to the root folder of the movie and renames them.
    '''
    # Define extensions to ignore
    ignore_extensions = {'.ini', '.exe', '.parts', '.xml', '.sqlite', '.xlsx', '.txt', '.jpg', '.mp4',
                     '.mp3', '.avi', '.mkv', '.flac', '.mov', '.mpeg', '.xvid', '.webm', '.flv', '.wmv'}

    movie_name = os.path.basename(movie_dir)
    for subtitle_file in subtitle_files:
        file_ext = os.path.splitext(subtitle_file)[1]
        if file_ext.lower() in ignore_extensions:
            continue

        language = extract_language(subtitle_file)
        if not language:
            logger.error(f"Could not extract language for {subtitle_file}")
            continue
        
        new_file_name = f"{movie_name}.{language}{file_ext}"
        new_file_path = os.path.join(movie_dir, new_file_name)
        shutil.move(subtitle_file, new_file_path)
        logger.info(f"Moved and renamed {subtitle_file} to {new_file_path}")

def edit_subtitle_files(root_folder):
    '''
    This function orchestrates the moving and renaming of subtitle files.
    '''
    movies_without_subtitle_files = []
    for dirpath, dirnames, filenames in os.walk(root_folder):
        subtitle_files = [os.path.join(dirpath, f) for f in filenames if f.endswith(('.srt', '.sub', '.idx'))]
        if not subtitle_files:
            movies_without_subtitle_files.append(os.path.basename(dirpath))
            continue
        
        move_subtitle_files_to_root(dirpath, subtitle_files)
    
    # Save the list of movies without subtitle files to a CSV
    pd.DataFrame(movies_without_subtitle_files, columns=['Movie']).to_csv('movies_without_subtitle_files.csv', index=False)

if __name__ == "__main__":
    root_folder_path = "E:\\Movie_edit_testing"
    logging.info(f"Starting program for folder {root_folder_path}")
    edit_subtitle_files(root_folder_path)
    logger.info("Finished editing subtitle files.")
