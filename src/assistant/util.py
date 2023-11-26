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

def get_all_assistants():
    assistants = openai.beta.assistants.list()
    logger.debug(f'Get all assistants: {assistants}')
    return assistants

def get_assistant_ids_from_names(assistant_names, strict=False):
    assistants = get_all_assistants()
    assistant_ids = []
    for assistant_name in assistant_names:
        matched_ids = []
        for assistant_data in assistants.data:
            if (strict and assistant_name == assistant_data.name) or (not strict and assistant_name in assistant_data.name) or (assistant_name == assistant_data.id):
                matched_ids.append(assistant_data.id)
        assistant_ids.append(matched_ids)
    logger.debug(f'Get assistant IDs from names: {assistant_ids}; {assistant_names}')
    return assistant_ids