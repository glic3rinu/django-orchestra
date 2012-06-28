import os


def execute_local(script):
    exit_code = os.system(script)
    if exit_code == 512: 
        raise os.error
    elif exit_code == 256: return 'warning'
    elif exit_code == 0: return 'success'
    else: return 'unknown'
    #TODO: handle the error code in windows.
