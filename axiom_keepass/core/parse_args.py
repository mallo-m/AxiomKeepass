#!/usr/bin/python3

import os
import ipaddress
from argparse import ArgumentParser
from impacket.examples.utils import parse_target

class AxiomArgParser():
    args = {}
    identity = {}

    @staticmethod
    def SetProgramArgs(a):
        AxiomArgParser.args = a

    @staticmethod
    def GetProgramArgs():
        return (AxiomArgParser.args)

    def __init__(self):
        #self._parser = ArgumentParser(description='Remotely dump keepass instances')
        self._parent_parser = ArgumentParser(add_help=False)
        self._parser = ArgumentParser(parents=[self._parent_parser])
        self._subparser = self._parser.add_subparsers(dest="mode", help="Functioning mode")

    def Parse(self):
        if self._parser is None:
            raise ValueError("AxiomArgParser was not properly initialized")

        self._parent_parser.add_argument("-hashes", "--hashes", help="LM:NT hash")

        self._parent_parser.add_argument(
            "-aesKey",
            "--aesKey",
            help="AES key to use for Kerberos Authentication",
            default=None
        )
        self._parent_parser.add_argument(
            "-k",
            action="store_true",
            help="Use kerberos authentication.",
            default=False
        )
        self._parent_parser.add_argument(
            "-dc-ip",
            "--dc-ip",
            help="IP Address of the domain controller",
            default=None
        )
        self._parent_parser.add_argument(
            "-no-pass",
            "--no-pass",
            action="store_true",
            help="Do not prompt for password",
            default=False
        )
        self._parent_parser.add_argument(
            "-t",
            "--threads",
            help="The number of threads to use, default: 10",
            type=int,
            default=10
        )
        self._parent_parser.add_argument(
            "target",
            help="Target machine or range [domain/]username[:password]@<IP, IP RANGE, FQDN or FILE>",
        )

        poison_parser = self._subparser.add_parser("poison", parents=[self._parent_parser])
        poison_parser.add_argument(
            "-kill-first",
            "--kill-first",
            action="store_true",
            default=False,
            help="Whether the attack should attempt to kill KeePass.exe processes before poisoning the installation"
        )
        poison_parser.add_argument(
            "-loot-method",
            "--loot-method",
            choices=["disk-drop", "upload", "dns"],
            default="disk-drop"
        )
        poison_parser.add_argument(
            "-upload-to",
            "--upload-to",
            type=str,
            help='Destination URL for upload exfiltration, only required if --loot-method=upload is provided'
        )
        poison_parser.add_argument(
            "-nameserver",
            "--nameserver",
            type=str,
            help="Exfiltration nameserver when using DNS loot-method"
        )

        pull_parser = self._subparser.add_parser("pull", parents=[self._parent_parser])
        pull_parser.add_argument(
            "-monitor",
            "--monitor",
            action="store_true",
            help="Run in monitor mode, will try to pull for new vaults every X seconds, where X is defined by --monitor-delay",
            default=False
        )
        pull_parser.add_argument(
            "-monitor-delay",
            "--monitor-delay",
            type=int,
            help="The delay in seconds between each pull when running in monitor mode",
            default=60
        )

        listen_parser = self._subparser.add_parser("listen", parents=[])
        listen_parser.add_argument(
            "-dns",
            "--dns",
            action="store_true",
            help="Switch to DNS listener",
            default=False
        )
        listen_parser.add_argument(
            "-port",
            "--port",
            type=int,
            help="What port the server listens on",
            default=9001
        )

        cleanup_parser = self._subparser.add_parser("cleanup", parents=[self._parent_parser])
        cleanup_parser.add_argument(
            "-kill-first",
            "--kill-first",
            action="store_true",
            default=False,
            help="Whether the cleanup agent should attempt to kill KeePass.exe processes before removing the DLL"
        )

        self.args = self._parser.parse_args()
        return (self.args)

    def Validate(self):
        if self.args is None:
            raise ValueError("You must parse arguments before validating them")

        if self.args.mode == "poison" \
            and self.args.loot_method == "upload" \
            and self.args.upload_to is None:
            raise ValueError("You must provide an exfiltration URL when using --loot-method=upload")

        if self.args.mode == "poison" \
            and self.args.loot_method == "dns" \
            and self.args.nameserver is None:
            raise ValueError("You must provide an exfiltration nameserver when using --loot-method=dns")

        if self.args.mode == "listen":
            return ({})

        domain, username, password, target = parse_target(self.args.target) # type: ignore
        if os.path.exists(target):
            result = []
            f = open(target, 'r')
            for l in f.readlines():
                l = l.strip()
                result.extend([str(ip) for ip in ipaddress.ip_network(l, strict=False).hosts()])
            f.close()
            target = result
        else:
            target = [str(ip) for ip in ipaddress.ip_network(target, strict=False).hosts()]
        if self.args.hashes and not password: # type: ignore
            lm_hash, nt_hash = self.args.hashes.split(":") # type: ignore
        else:
            nt_hash = ""
            lm_hash = ""

        if self.args.aesKey is None: # type: ignore
            aesKey = ""
        else:
            aesKey = self.args.aesKey # type: ignore
            self.args.k = True # type: ignore

        if (
            password == ""
            and username != ""
            and nt_hash == ""
            and lm_hash == ""
            and aesKey == ""
            and not self.args.no_pass # type: ignore
        ):
            from getpass import getpass

            password = getpass("Password:")

        AxiomArgParser.SetProgramArgs(self.args)
        self.identity = {
            "domain": domain,
            "username": username,
            "password": password,
            "target": target,
            "dc_ip": self.args.dc_ip, # type: ignore
            "nt_hash": nt_hash,
            "lm_hash": lm_hash,
            "aesKey": aesKey,
            "useKerberos": self.args.k # type: ignore
        }
        return (self.identity)

