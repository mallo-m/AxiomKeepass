#!/usr/bin/python3

import os
from io import BytesIO

def download(smbClient, thread_index, filepath: str, savepath: str, silent=False):
    buffer = BytesIO()
    smbClient.getFile("C$", filepath, buffer.write)
    if not silent:
        print(f"[THREAD {thread_index}][+] Download {os.path.basename(savepath)} file with {len(buffer.getvalue())} bytes")

    f = open(savepath,'wb')
    f.write(buffer.getvalue())
    f.close()
    if not silent:
        print(f"[THREAD {thread_index}][+] {os.path.basename(savepath)} dropped to disk")

