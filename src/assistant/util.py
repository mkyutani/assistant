import openai
from assistant.environment import logger

def get_all_files(purpose=openai._types.NotGiven):
    files = openai.files.list(purpose=purpose)
    logger.debug(f'Get all files: {files}')
    return files

def get_file_ids_from_names(filenames, purpose=openai._types.NotGiven):
    files = get_all_files(purpose=purpose)
    file_ids = []
    all_matched = True
    for filename in filenames:
        for file_data in files.data:
            if filename in file_data.filename:
                file_ids.append(file_data.id)
                break
        else:
            file_ids.append(None)
            all_matched = False
    logger.debug(f'Get file IDs from names: {file_ids}; {all_matched}; {filenames}')
    return (file_ids, all_matched)

