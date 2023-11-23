all:
	@echo nothing to do, just run \"sudo make install\"

install:
	install -m 0755 afl-* /usr/local/bin
