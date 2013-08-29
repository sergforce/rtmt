#include <time.h>
#include <stdlib.h>
#define WITH_RTMD
#include <RTMD.h>

int main(int argc, char** argv)
{
	time_t tm;
	int i;
	
	RTMD_INIT(1200000);
	
	for (i = 0; i < 800000; i++) {
		RTMD_SET("time");
		time(&tm);
		RTMD_CLEAR("time");
	}
	
	RTMD_FLUSH("test_time_data.rtmd");
	return 0;
}
