# Makefile to send this project to Szam
SHELL=/usr/bin/env /bin/bash

all:	send

send:	send_zamok
send_zamok:
	CP --exclude=.ipynb_checkpoints --exclude=.git ./ ${Szam}publis/Discord-bot-to-add-spoiler-to-any-code-snippet.git/
