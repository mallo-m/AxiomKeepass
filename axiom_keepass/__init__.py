#!/usr/bin/python3

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.core.worker import ThreadWorker
from axiom_keepass.utils.listener import run_http_listener, run_dns_listener

def main():
    parser = AxiomArgParser()
    args = parser.Parse()
    identity = parser.Validate()

    if args.mode == "listen" and args.dns is False:
        run_http_listener(args.port)
    elif args.mode == "listen" and args.dns is True:
        run_dns_listener(args.port)
    else:
        thread_count = AxiomArgParser.GetProgramArgs().threads #type: ignore
        target_count = len(identity['target'])
        for i in range(min(thread_count, target_count)):
            _t = ThreadWorker(identity, i, thread_count, identity['target'], target_count)
            _t.start()

if __name__ == "__main__":
    main()

