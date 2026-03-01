#!/usr/bin/python3

import sys
from impacket import smb
from impacket.smbconnection import SMBConnection, SessionError

def login(args: dict, target: str, thread_index: int):
    try:
        smbClient = SMBConnection(
            target,
            target,
            timeout=2
        )

        if args['useKerberos']:
            smbClient.kerberosLogin(
                args['username'],
                args['password'],
                args['domain'],
                args['lmhash'],
                args['nthash'],
                args['aesKey'],
                args['dc_ip'],
            )
        else:
            smbClient.login(
                args['username'],
                args['password'],
                args['domain'],
                args['lm_hash'],
                args['nt_hash']
            )

        print(f"[THREAD {thread_index}][+] Successful login to {smbClient.getRemoteHost()}")
        return (smbClient)
    except Exception as e:
        print(f"[THREAD {thread_index}][!] {target}: {str(e)}, adding to bad targets...")

    return (None)

