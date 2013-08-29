LDFLAGS=-lpthread -lrt
CFLAGS=-Wall -O3 -I..
RTMD_FILES=../RTMD.c ../RTMD.h

test_mutex: test_mutex.c $(RTMD_FILES)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

