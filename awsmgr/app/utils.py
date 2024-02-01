import shutil

def is_command_available(name):
    return shutil.which(name) is not None