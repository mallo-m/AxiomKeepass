#!/usr/bin/python3

import os
from io import BytesIO

def download(smbClient, filepath: str, savepath: str):
    buffer = BytesIO()
    smbClient.getFile("C$", filepath, buffer.write)
    print(f"[+] Download {os.path.basename(savepath)} file with {len(buffer.getvalue())} bytes")

    f = open(savepath,'wb')
    f.write(buffer.getvalue())
    f.close()
    print(f"[+] {os.path.basename(savepath)} dropped to disk")

