import os
import logging
import subprocess
from mutagen import File

# Configure logging
logger = logging.getLogger()  # Get the root logger
logger.setLevel(logging.INFO)

# File Handler - logs to a file
file_handler = logging.FileHandler('edit_movie_tags.log')
file_format = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# Stream Handler - logs to the console
stream_handler = logging.StreamHandler()
stream_format = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)

def iterate_files(path, ignore_file_ext):
    for root, dirs, files in os.walk(path):
        for file in files:
            if not any(file.lower().endswith('.' + ext) for ext in ignore_file_ext):
                yield os.path.join(root, file)
                

def get_current_metadata_title(file_path):
    # This function uses FFprobe to get the current title metadata from the file
    try:
        ffprobe_path = 'D:/PyScripts/movie_list/ffprobe.exe'  # Adjust to your actual ffprobe path
        result = subprocess.run(
            [ffprobe_path, "-loglevel", "error", "-select_streams", "v:0",
            "-show_entries", "format_tags=title", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting metadata from file {file_path}: {e}")
        return None


def edit_avi_metadata(file_path, new_title):
    try:
        logging.info(f"In Function edit_avi_metadata and checking metadata for AVI file: {file_path}")
        current_title = get_current_metadata_title(file_path)
        if current_title == new_title:
            logging.info(f"Title already matches for {file_path}, skipping metadata update.")
            return

        ffmpeg_path = 'D:/PyScripts/movie_list/ffmpeg.exe'  # Replace with your actual FFmpeg path
        cmd = [
            ffmpeg_path,
            '-fflags', '+genpts',  # Generate PTS if missing
            '-i', file_path,  # Just pass file_path directly
            '-metadata', f'title={new_title}',
            '-codec', 'copy',
            f'{file_path}.temp.avi'
        ]
        
        logging.info(f"Running FFmpeg command: {cmd}. Updating metadata for AVI file: {file_path} and saving to {file_path}.temp.avi")
        
        # Run the FFmpeg command
        subprocess.run(cmd, shell=True, check=True, cwd=os.path.dirname(file_path))
        
        # Replace original file with the new file
        temp_file = f"{file_path}.temp.avi"
        os.replace(temp_file, file_path)
        logging.info(f"Metadata updated for AVI file: {file_path}")

    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error for file {file_path}: {e}")
    except Exception as e:
        logging.error(f"General error updating file {file_path}: {e}")



def update_metadata(file_path):
    try:
        # Check if file is AVI, use FFmpeg
        if file_path.lower().endswith('.avi'):
            logging.info(f"Checking metadata for AVI file: {file_path}")
            file_name = os.path.basename(file_path)
            logging.info(f"File name: {file_name}")
            title_without_extension, _ = os.path.splitext(file_name)
            logging.info(f"Title without extension: {title_without_extension}")
            edit_avi_metadata(file_path, title_without_extension)
            logging.info(f"Finished updating metadata for AVI file: {file_path}\n")
            return
        media_file = File(file_path, easy=True)
        if media_file is None:
            logging.warning(f"Cannot handle file format: {file_path}\n")
            return

        # Extract file name without extension to compare with title tag
        file_name = os.path.basename(file_path)
        title_without_extension, ext = os.path.splitext(file_name)

        # Check if 'title' tag exists and matches the file name without extension
        if 'title' in media_file:
            if media_file['title'][0] == title_without_extension:
                logging.info(f"Title already matches file name for {file_path}, skipping\n")
                return

        # Rename title to match the file name without extension
        original_title = media_file.get('title', '[No Title]')
        media_file['title'] = title_without_extension
        logging.info(f"Title changed from: '{original_title}' to: '{title_without_extension}' in file: {file_path}")

        # Remove comments
        if 'comment' in media_file:
            del media_file['comment']
            logging.info(f"Removed comment from file {file_path}\n")

        media_file.save()

    except Exception as e:
        logging.error(f"Error updating file {file_path}: {e}\n")


if __name__ == "__main__":
    
    ignore_file_ext = ['ini', 'sub', 'exe', 'parts', 'idx', 'srt', 'xml', 'sqlite', 'xlsx', 'txt', 'jpg']
    nas_path = '//10.0.0.148/Movies'  
    local_path = 'E:\Videos'  
    for file in iterate_files(local_path, ignore_file_ext):
        update_metadata(file)
    msg = f"Finished updating metadata for files in {local_path}"
    logging.info(msg)

    # edit_avi_metadata('E:\Videos\Drugs Inc - Hallucinogens (2012).avi','Hallucinogens (2012)')