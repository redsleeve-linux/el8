VERSION ?= 20.1.4
SANITIZE ?= 1

DIRNAME = mesa-${VERSION}

all: archive

clean:
	rm -rf $(DIRNAME)/
	rm -f mesa-${VERSION}.tar.xz

clone: clean
	curl -O https://archive.mesa3d.org/mesa-${VERSION}.tar.xz
	tar xf mesa-${VERSION}.tar.xz

sanitize: clone vl_mpeg12_decoder.c vl_decoder.c
ifdef SANITIZE
	cat < vl_mpeg12_decoder.c > $(DIRNAME)/src/gallium/auxiliary/vl/vl_mpeg12_decoder.c
	cat < vl_decoder.c > $(DIRNAME)/src/gallium/auxiliary/vl/vl_decoder.c
endif

archive: clone sanitize
	tar caf ${DIRNAME}.tar.xz ${DIRNAME}
