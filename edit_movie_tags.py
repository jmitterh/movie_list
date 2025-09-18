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

def iterate_files(path: str, ignore_file_ext: list)-> str:
    '''
    Iterate through all files in the given path and ignore files with the given extensions
    variables:
        path: path to iterate through
        ignore_file_ext: list of file extensions to ignore
    returns: file_path
    '''
    for root, dirs, files in os.walk(path):
        for file in files:
            if not any(file.lower().endswith('.' + ext) for ext in ignore_file_ext):
                yield os.path.join(root, file)
                
# currently not used
def get_current_metadata_title(file_path:str)-> str:
    '''
    Get the current title from the file
    variables:
        file_path: path to the file
    returns: title
    '''
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


def get_metadata_title_and_comments(file_path:str)-> str:
    '''
    Get the current title and comments from the file
    variables:
        file_path: path to the movie file
    returns: title, comments
    '''
    try:
        ffprobe_path = 'D:/PyScripts/movie_list/ffprobe.exe'  # Adjust to your actual ffprobe path
        # Command to get title and comments
        command = [
            ffprobe_path, "-loglevel", "error", "-select_streams", "v:0",
            "-show_entries", "format_tags=title:format_tags=comment", "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.stdout.decode('utf-8').strip()
        # Split the output by newline to get separate metadata entries
        metadata = output.split('\n')
        title = metadata[0] if len(metadata) > 0 else None
        comments = metadata[1] if len(metadata) > 1 else None
        return title, comments
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting metadata from file {file_path}: {e}")
        return None, None


def edit_video_metadata(file_path: str, new_title: str)-> None:
    '''
    Edit the video metadata using FFmpeg
    variables:
        file_path: path to the video file
        new_title: new title for the video file
    returns: None
    '''
    try:
        logging.info(f"Checking metadata for video file: {file_path}")
        # get the current title and comments
        current_title, current_comments = get_metadata_title_and_comments(file_path)
        if current_title == new_title and (current_comments is None or current_comments == ''):
            logging.info(f"Title already matches for {file_path}, and no comments in the comments section. Skipping metadata update.")
            return
        
        logging.info(f"Current title: {current_title}, new title: {new_title}, current comments: {current_comments}")
        file_extension = os.path.splitext(file_path)[1]
        temp_file = f"{file_path}.temp{file_extension}"
        ffmpeg_path = 'D:/PyScripts/movie_list/ffmpeg.exe'  # Update this path
        cmd = [
            ffmpeg_path,
            '-fflags', '+genpts',
            '-i', file_path,
            '-metadata', f'title={new_title}',
            '-metadata', 'comment=',  # This line will clear the comment tag
            '-codec', 'copy',
            '-y',  # Overwrite without asking
            temp_file
        ]

        logging.info(f"Running FFmpeg command: {cmd}. Updating metadata for video file: {file_path} and saving to {temp_file}")
        subprocess.run(cmd, shell=True, check=True, cwd=os.path.dirname(file_path))
        os.replace(temp_file, file_path)
        logging.info(f"Metadata updated for video file: {file_path}")
        return
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error for file {file_path}: {e}")
    except Exception as e:
        logging.error(f"General error updating file {file_path}: {e}")


def update_metadata(file_path: str)-> None:
    '''
    This function will update the metadata for the given file
    '''
    video_file_extensions = ['.avi', '.mkv', '.mp4', '.mov', '.mpeg', '.xvid', '.webm', '.flv', '.wmv','.ass'] # Add other extensions if needed
    try:
        # Check file extension, use FFmpeg for AVI, MKV, and other video formats
        file_extension = os.path.splitext(file_path)[1]
        if file_extension.lower() in video_file_extensions:  
            logging.info(f"Checking metadata for {file_extension} file: {file_path}")
            file_name = os.path.basename(file_path)
            # title of the file without extension
            title_without_extension, _ = os.path.splitext(file_name)
            # Check if title already matches the file name without extension
            edit_video_metadata(file_path, title_without_extension)
            return
    except Exception as e:
        logging.error(f"Error updating file via update metadata function, first if block: {file_path}: {e}\n")

    try:
        # For formats handled by Mutagen
        media_file = File(file_path, easy=True)
        if media_file is None:
            logging.warning(f"Cannot handle file format: {file_path}")
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
        return
    except Exception as e:
        logging.error(f"Error updating file via formats handled by Mutagen, second if block: {file_path}: {e}\n")


if __name__ == "__main__":
    
    ignore_file_ext = ['.ini', '.sub', '.exe', '.parts', '.idx', '.srt', '.xml', '.sqlite', '.xlsx', '.txt', '.jpg']
    
    nas_path = '//10.0.0.148/Media/Movies'  
    local_path = 'E:\Videos'
    single_path = "E:/Videos/Ninja Scroll (1993) 1080p"
    list_path = ['E:\Videos\Godzilla Minus One (2023) 1080p']
    
    for path in list_path:
        for file in iterate_files(path, ignore_file_ext):
            update_metadata(file)
    msg = f"Finished updating metadata for files in {list_path}"
    logging.info(msg)