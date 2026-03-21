#!/usr/bin/python3

# Checks if KeePass is running by attempting to delete the file KeePass.exe
# If we get a SHARING_VIOLATION, that means that a process has a lock on the file
# so we know that KeePass is running
# Yes it's ugly but I don't have another way to check for this that doesn't involve
# running commands on the remote target
def check_if_running():
    pass
