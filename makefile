CC=i686-w64-mingw32-g++
CFLAGS=-o build/rev.exe -lws2_32 -s -ffunction-sections -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc
BUILD_DIR=build

build_rev: rev.c
	$(shell mkdir -p $(BUILD_DIR))
	$(CC) rev.c $(CFLAGS)