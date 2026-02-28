#!/usr/bin/python3

from axiom_keepass.core.parse_args import AxiomArgParser
from axiom_keepass.core.worker import ThreadWorker

def main():
    parser = AxiomArgParser()
    parser.Parse()
    args = parser.Validate()

    thread_count = AxiomArgParser.GetProgramArgs().threads #type: ignore
    target_count = len(args['target'])
    for i in range(min(thread_count, target_count)):
        _t = ThreadWorker(args, i, thread_count, args['target'], target_count)
        _t.start()

if __name__ == "__main__":
    main()

