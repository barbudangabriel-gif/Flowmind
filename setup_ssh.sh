#!/bin/bash
mkdir -p /root/.ssh
chmod 700 /root/.ssh
curl -o /root/.ssh/authorized_keys https://raw.githubusercontent.com/barbudangabriel-gif/Flowmind/main/flowmind_ssh_key.pub
chmod 600 /root/.ssh/authorized_keys
echo GATA SSH key instalata
cat /root/.ssh/authorized_keys
