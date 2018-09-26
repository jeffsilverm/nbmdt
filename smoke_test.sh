#! /bin/bash
# A smoke test of the nbmdt.py program
success=0
if ! python3 nbmdt.py --boot; then success=1; fi
if ! python3 nbmdt.py -b; then success=1; fi
if ! python3 nbmdt.py --monitor 20080; then success=1; fi
if ! python3 nbmdt.py -m 20080; then success=1; fi
if ! python3 nbmdt.py --diagnose xyzzy.json; then success=1; fi
if ! python3 nbmdt.py -d xyzzy.json; then success=1; fi
if ! python3 nbmdt.py --test ethernet=eno1; then success=1; fi
if ! python3 nbmdt.py -t ethernet=eno1; then success=1; fi
if [ $success -eq 0 ] ; then echo "smoke test PASSES"; else echo "smoke test **FAILS******"; fi
exit $success


