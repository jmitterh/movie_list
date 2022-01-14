import os
import pandas as pd


# files within directory
def files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


# folders within directory
def folders(path):
    for folder_name in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder_name)):
            yield folder_name


if __name__ == "__main__":
    filepath = 'E:\Videos'
    dict = {}
    movies_list = []
    folder_list = []
    # movie file names
    for file in files(filepath):
        if '.mp4' in file or '.avi' in file or '.mkv' in file:
            # quick formatting
            file = file.replace(".mp4", "")
            file = file.replace(".avi", "")
            file = file.replace(".mkv", "")
            file = file.replace("720p", "")
            file = file.replace("1080p", "")
            file = file.replace("  ", " ")  # remove double whitespace
            file = file.strip()
            file = file.lower()
            # print(f"file name: {file}")
            movies_list.append(file)

    # duplicate movies
    seen = set()
    dupes_file = [x for x in movies_list if x in seen or seen.add(x)]
    # print(f'duplicate movies:\n{dupes_file}')

    # folder names
    for name in folders(filepath):
        # quick formatting
        name = name.replace("720p", "")
        name = name.replace("1080p", "")
        name = name.replace("  ", " ")  # remove double whitespace
        name = name.strip()
        name = name.lower()
        # print(f"folder name:{name}")
        folder_list.append(name)

    # duplicate folders
    seen = set()
    dupes_folders = [x for x in folder_list if x in seen or seen.add(x)]
    # print(f'duplicate folders:\n{dupes_folders}')

    # list comprehension: filter files and folders with the same name
    delete_movies = [x for x in folder_list if x in movies_list]
    # for x in delete_movies:
    #     print(f'delete this movie file: {x}')

    # list comprehension: movies to download again, filters files that do not have the same name as folders
    download_movies = [x for x in movies_list if x not in folder_list]
    # for x in download_movies:
    #     print(f'download: {x}')

    # adding list to a dictionary
    dict['duplicate_movies'] = dupes_file
    dict['duplicate_folders'] = dupes_folders
    dict['delete_movie_file'] = delete_movies
    dict['download'] = download_movies

    # for different array size in a dictionary to DF
    # df = pd.DataFrame.from_dict(dict, orient='index')
    # df = df.transpose()
    df = pd.DataFrame({key: pd.Series(value) for key, value in dict.items()})
    # print(df)
    df.to_csv('movie_list.csv', index=False)
