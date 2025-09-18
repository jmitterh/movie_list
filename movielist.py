import os
import pandas as pd
import datetime as dt


# files within directory
def iterate_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file


# folders within directory
def iterate_folders(path):
    for folder_name in os.listdir(path):
        if os.path.isdir(os.path.join(path, folder_name)):
            yield folder_name


if __name__ == "__main__":
    filepath = 'E:\Videos'
    dict = {}
    ignore_file_exe = ['ini','sub','exe','parts','idx','srt','xml','sqlite','xlsx','txt','jpg','sfv','sub']
    # different file extensions
    file_extension_list = set()
    for (path, dirs, files) in os.walk(filepath):
        path = path.replace('\\', '/')
        for file in files:
            try:
                file_extension = file.split('.')[-1]
                # if file_extension in ['rmvb']:
                #     print(f'{path}/{file}')
                if file_extension not in ignore_file_exe:
                    file_extension_list.add(file_extension)
            except Exception as e:
                print(f'Error: File Extension: {e}\n{path}/{file}')
                continue
    file_extension_list =list(file_extension_list)
    # print(file_extension_list)

    # files with 720 or 1080p
    all_movies = []
    movies720_list = []
    movies1080_list = []
    movie_quality_not_defined = []
    for (path, dirs, files) in os.walk(filepath):
        path = path.replace('\\', '/')
        for file in files:
            try:
                splits = file.split('.')
                file = splits[0]
                file = file.strip()
                ext = splits[-1]
                if ext not in ignore_file_exe:
                    if file.endswith('720p'):
                        movies720_list.append(file+'.'+ext)
                    elif file.endswith('1080p'):
                        movies1080_list.append(file+'.'+ext)
                    else:
                        movie_quality_not_defined.append(file+'.'+ext)
                    # add movies
                    file = file.replace("720p", "")
                    file = file.replace("1080p", "")
                    file = file.replace("  ", " ")  # remove double whitespace
                    file = file.lower()
                    all_movies.append(file)
            except Exception as e:
                print(f'Error: File Extension: {e}\n{path}/{file}')

    # duplicate movies of both with folders and without
    seen = set()
    all_movies_duplicates = [x for x in all_movies if x in seen or seen.add(x)]
    # print(f'duplicate movies:\n{dupes_file}')



    # movie file names not in folders
    movies_list_not_in_folder = []
    for file in iterate_files(filepath):
        splits = file.split('.')
        ext = splits[-1]
        if ext in file_extension_list:
            # quick formatting
            file = splits[0]
            file = file.replace("720p", "")
            file = file.replace("1080p", "")
            file = file.replace("  ", " ")  # remove double whitespace
            file = file.strip()
            file = file.lower()
            # print(f"file name: {file}")
            movies_list_not_in_folder.append(file)

    # duplicate movies files not in folder
    seen = set()
    dupes_movies_not_in_folder = [x for x in movies_list_not_in_folder if x in seen or seen.add(x)]
    # print(f'duplicate movies:\n{dupes_file}')



    # folder names only
    folder_list = []
    for name in iterate_folders(filepath):
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
    folder_n_file_same_name = [x for x in folder_list if x in movies_list_not_in_folder]
    # for x in delete_movies:
    #     print(f'delete this movie file: {x}')

    # list comprehension: movies to download again, filters files that do not have the same name as folders
    movies_not_in_folder = [x for x in movies_list_not_in_folder if x not in folder_list]
    # for x in download_movies:
    #     print(f'download: {x}')



    # adding list to a dictionary
    dict['duplicate_movies_not_in_folders'] = dupes_movies_not_in_folder
    dict['duplicate_folders'] = dupes_folders
    dict['delete_movie_file_duplicate_from_folder_name'] = folder_n_file_same_name
    dict['all_files_duplicate_movies'] = all_movies_duplicates # files with and without folders
    dict['movies_not_in_folder'] = movies_not_in_folder
    dict['720p_movies'] = movies720_list
    dict['1080p_movies'] = movies1080_list
    dict['undefined_quality_movies'] = movie_quality_not_defined
    dict['all_movie_files'] = all_movies

    # for different array size in a dictionary to DF
    # df = pd.DataFrame.from_dict(dict, orient='index')
    # df = df.transpose()
    df = pd.DataFrame({key: pd.Series(value, dtype='object') for key, value in dict.items()})
    # print(df)
    datetime = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    df.to_csv(f'./output/movie_list_{datetime}.csv', index=False)

print('finished')
