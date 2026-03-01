#!/usr/bin/python3

import os
from io import BytesIO

def download(smbClient, thread_index, filepath: str, savepath: str, silent=False):
    buffer = BytesIO()
    try:
        smbClient.getFile("C$", filepath, buffer.write)
    except Exception as e:
        if "STATUS_OBJECT_NAME_NOT_FOUND" in str(e):
            print(f"[THREAD {thread_index}][!] Failed to download {os.path.basename(savepath)} from {smbClient.getRemoteHost()}: FILE_NOT_FOUND")
        else:
            print(f"[THREAD {thread_index}][!] Failed to download {os.path.basename(savepath)} from {smbClient.getRemoteHost()}: {str(e)}")
        return (False)

    if not silent:
        print(f"[THREAD {thread_index}][+] Download {os.path.basename(savepath)} file with {len(buffer.getvalue())} bytes")

    f = open(savepath,'wb')
    f.write(buffer.getvalue())
    f.close()
    if not silent:
        print(f"[THREAD {thread_index}][+] {os.path.basename(savepath)} dropped to disk")
    return (True)

