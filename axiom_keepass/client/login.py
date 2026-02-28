#!/usr/bin/python3

import sys
from impacket import smb
from impacket.smbconnection import SMBConnection, SessionError

def login(args: dict):
    try:
        smbClient = SMBConnection(
            args['target'],
            args['target'],
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
    except Exception as e:
        print(f"[-] {str(e)}")
        sys.exit(1)

    return (smbClient)

