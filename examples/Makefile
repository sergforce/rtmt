LDFLAGS=-lpthread -lrt
CFLAGS=-Wall -O3 -I..
RTMD_FILES=../RTMD.c ../RTMD.h

.PHONY: all

all: test_mutex test_time

test_mutex: test_mutex.c $(RTMD_FILES)
	$(CC) $(CFLAGS)  -o $@ $^ $(LDFLAGS)

test_time: test_time.c $(RTMD_FILES)
	$(CC) $(CFLAGS)  -o $@ $^ $(LDFLAGS)



