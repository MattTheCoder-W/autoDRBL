#!/bin/bash

if [ ! "$EUID" -lt 2 ]; then
	echo "You are not root!"
	exit
fi

wget -q http://drbl.org/GPG-KEY-DRBL -O- | sudo apt-key add -
sudo echo "deb http://free.nchc.org.tw/drbl-core drbl stable" >> /etc/apt/sources.list
sudo apt update
sudo apt install drbl

echo "Now run drblsrv -i or drblpush -i for futher configuration..."
