install:
	cp cerb.py /usr/local/bin/cerb
	chmod +x /usr/local/bin/cerb
	cp vim/cerb.vim ~/.vim/cerb.vim
	mkdir -p ~/.vim/syntax ~/.vim/ftdetect
	cp vim/syntax:cerb.vim ~/.vim/syntax/cerb.vim
	cat vim/filetype.vim >> ~/.vim/filetype.vim
	cp vim/ftdetect:cerb.vim ~/.vim/ftdetect/cerb.vim
uninstall:
	rm /usr/local/bin/cerb
.PHONY: install uninstall
