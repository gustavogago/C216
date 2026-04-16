#!/bin/sh
pytest -q -s -p no:cacheprovider tests | tee test-log.txt
