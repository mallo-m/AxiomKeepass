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
        self._parser = ArgumentParser(description='Remotely dump keepass instances')

    def Parse(self):
        if self._parser is None:
            raise ValueError("AxiomArgParser was not properly initialized")

        self._parser.add_argument("-hashes", "--hashes", help="LM:NT hash")

        self._parser.add_argument(
                "-aesKey",
                "--aesKey",
                help="AES key to use for Kerberos Authentication"
        )

        self._parser.add_argument(
            "-k",
            action="store_true",
            help="Use kerberos authentication.",
        )

        self._parser.add_argument(
            "-dc-ip",
            "--dc-ip",
            help="IP Address of the domain controller"
        )

        self._parser.add_argument(
            "-no-pass",
            "--no-pass",
            action="store_true",
            help="Do not prompt for password"
        )

        self._parser.add_argument(
            "-t",
            "--threads",
            help="The number of threads to use, default: 10",
            type=int,
            default=10
        )

        self._parser.add_argument(
            "-pull",
            "--pull",
            action="store_true",
            help="Run in pull mode, checks if any vault has been exported and downloads them",
        )

        self._parser.add_argument(
            "-monitor",
            "--monitor",
            action="store_true",
            help="Run in monitor mode, will try to pull for new vaults every X seconds, where X is defined by --monitor-delay",
            default=False
        )

        self._parser.add_argument(
            "-monitor-delay",
            "--monitor-delay",
            type=int,
            help="The delay in seconds between each pull when running in monitor mode",
            default=60
        )

        self._parser.add_argument(
            "-kill-first",
            "--kill-first",
            action="store_true",
            default=False,
            help="Whether the attack should attempt to kill KeePass.exe processes before poisoning the installation"
        )

        self._parser.add_argument(
            "target",
            help="Target machine or range [domain/]username[:password]@<IP, IP RANGE, FQDN or FILE>",
        )

        self.args = self._parser.parse_args()

    def Validate(self):
        if self.args is None:
            raise ValueError("You must parse arguments before validating them")

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

