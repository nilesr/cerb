install:
	cp cerb.py /usr/local/bin/cerb
	chmod +x /usr/local/bin/cerb
uninstall:
	rm /usr/local/bin/cerb
.PHONY: install uninstall
