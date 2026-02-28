#!/usr/bin/python3

import re
import sys
import axiom_keepass

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(axiom_keepass.main())

