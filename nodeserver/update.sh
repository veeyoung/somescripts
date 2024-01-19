#!/bin/bash
cd /home/user/nodeserver/convert2clash/
echo "../nodes.txt;../freesub.txt" |./convertClash.py -O ../config.yaml
