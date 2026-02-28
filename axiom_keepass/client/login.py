#!/usr/bin/python3

import sys
from impacket import smb
from impacket.smbconnection import SMBConnection, SessionError

def login(args: dict, target: str):
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

    return (smbClient)

