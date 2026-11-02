#!/bin/bash

sudo nmcli con up "Wired connection 1"
ping -c 3 192.168.1.10

exit 0