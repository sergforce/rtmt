#include <stdio.h>
#ifndef WIN32
#include <sys/time.h>
#endif
#include <stdlib.h>
#include <string.h>

#ifdef __hpux
#include <sys/types.h>
#define get64(x)  (x)
#elif defined(_MSC_VER)
typedef int int32_t;
typedef unsigned int uint32_t;

typedef __int64 int64_t;
typedef unsigned __int64 uint64_t;

//#define get64(x)  ((x).QuadPart)
#define get64(x)  (x)
#else
#include <stdint.h>
#define get64(x)  (x)
#endif

////////////////////////////////////////
// Configuration

#define RTMD_THREAD_SAFE
//#define NO_CYCLE
//#define RTMD_SAFE_ALIGN
//#define RTMD_NO_SSE

// End of configuration
////////////////////////////////////////

// Autodetect SSE support
#ifndef RTMD_NO_SSE
#ifdef __SSE2__
#define RTMD_USE_SSE2
#endif
#ifdef __SSE4_1__
#define RTMD_USE_SSE4
#endif
#endif


#if defined(RTMD_USE_SSE4) && !defined(RTMD_USE_SSE2)
# define RTMD_USE_SSE2
#endif

#ifndef WITH_RTMD
#define WITH_RTMD
#endif
#include "RTMD.h"


#ifdef RTMD_USE_SSE4
#include <smmintrin.h>
#endif
#ifdef RTMD_USE_SSE2
#include <emmintrin.h>
#endif


#define RTMD_MAX_NAME		16

#define RTMD_FLAG_GTOFDAY  'G'
#define RTMD_FLAG_CYCLE    'C'
#define RTMD_FLAG_CYCLEINI 'I'

typedef struct RTMD_Node {
    char      name[RTMD_MAX_NAME];
    //char      cycleFlag;

    union {
        struct {
            uint32_t   secs;
            uint32_t   usecs;
        } _tval;
        uint64_t       tick;
    } _unsec;

    union {
        struct {
            uint32_t   lineNumber;
            uint32_t   val;
        } _sln;
        uint64_t       val64;
    } _unval;
} RTMD_Node_t;


#ifndef NO_CYCLE
# include "cycle.h"
# ifdef WIN32
#  define EXTRA_SPACE (1024*1024)
# else
#  define EXTRA_SPACE (1024)
# endif
#else
# define EXTRA_SPACE 0
#endif

#ifdef WIN32
#define gettimeofday  gettimeofday_port

#include <windows.h>
NTSTATUS (WINAPI *NtQuerySystemTimePtr)(_Out_  PLARGE_INTEGER SystemTime);

int gettimeofday_port(struct timeval* ptv, void* _unsigned)
{
    LARGE_INTEGER intl;
    NTSTATUS st = NtQuerySystemTimePtr(&intl);
    if (st != 0) {
        return -1;
    }

    ptv->tv_sec  = (long)(((intl.QuadPart - 11644473600000000Ui64) / 10000000) - 1890091648);
    ptv->tv_usec = (intl.QuadPart % 10000000) / 10;

    return 0;
}
#endif

#ifdef __GNUC__
#define likely(x)       __builtin_expect((x),1)
#define unlikely(x)     __builtin_expect((x),0)
#else
#define likely(x)       (x)
#define unlikely(x)     (x)
#endif

#define  secs       _unsec._tval.secs
#define  usecs      _unsec._tval.usecs
#define  val        _unval._sln.val
#define  lineNumber _unval._sln.lineNumber
#define  tick       _unsec.tick
#define  val64      _unval.val64



#if _POSIX_C_SOURCE >= 200112L || _XOPEN_SOURCE >= 600
static void* node_alloc(size_t size)
{
    void* mem = NULL;
    int res = posix_memalign(&mem, sizeof(RTMD_Node_t), size*sizeof(RTMD_Node_t));
    if (res)
	perror("posix_memalign");
    return mem;
}
#define node_free(x)   free(x)
#elif _MSC_VER
#define node_alloc(size)  _aligned_malloc(size*sizeof(RTMD_Node_t),sizeof(RTMD_Node_t))
#define node_free(x)   _aligned_free(x)
#else
//#warning Compiling without posix_memalign
#define node_alloc(x)  malloc((x)*sizeof(RTMD_Node_t))
#define node_free(x)   free(x)
#endif

/* Need to be volatile for proper work from signal handlers */
static RTMD_Node_t*         mem = 0;
static unsigned             count = 0;
static char                 dummy0[64];  //cache line separator
static volatile unsigned    ptr = 0;
static char                 dummy1[64];  //cache line separator


#if defined(RTMD_SAFE_ALIGN) || defined(RTMD_USE_SSE2)
# ifdef RTMD_USE_SSE2
#  define FAST_STORE_NAME_1(from, to, i)   \
      __m128i _tmp_name = _mm_loadu_si128((__m128i*)from)
#  ifdef RTMD_USE_SSE4
#   define FAST_STORE_NAME_2(from, to, i)   \
     _mm_store_si128((__m128i*)to, _mm_insert_epi8(_tmp_name, (i), 15))
#  else
#   define FAST_STORE_NAME_2(from, to, i)   \
     _mm_store_si128((__m128i*)to, _mm_insert_epi16(_tmp_name, (i) << 8, 7))
#  endif
# else
#  define FAST_STORE_NAME_1(from, to, i)
#  define FAST_STORE_NAME_2(from, to, i)   \
    (strncpy(to, from, RTMD_MAX_NAME - 1), \
    to[15] = i)
# endif
#else
# define FAST_STORE_NAME_1(from, to, i)
# define FAST_STORE_NAME_2(from, to, i)                       \
    (*((int64_t * )(to)) = *((const int64_t * )from),         \
     *((int64_t * )(&to[8])) = *((const int64_t * )&from[8]), \
     to[15] = i)

#endif


/*
 * You can use ' slot = ptr++; ' instead the instruction above,
 * but this doesn't guarantee proper work in a multi-thread application
 */

#ifdef __hpux
# define INCREMENT_SLOT(ptr)        ptr++
#else
# ifdef RTMD_THREAD_SAFE
#  if defined(_MSC_VER)
#   define INCREMENT_SLOT(ptr)      (_InterlockedIncrement(&ptr) - 1)
#  else
#   define INCREMENT_SLOT(ptr)      __sync_fetch_and_add(&ptr, 1)
#  endif
# else
#  define INCREMENT_SLOT(ptr)      ptr++
# endif
#endif



int RTMD_IsFull(void) {
	return ptr==count;
}

void RTMD_InitStorage(unsigned max)
{
	int i;
	if (mem != NULL)
		return;

	memset(dummy0, 0, sizeof(dummy0));
	memset(dummy1, 0, sizeof(dummy1));
	
#ifdef WIN32
    NtQuerySystemTimePtr = (NTSTATUS (WINAPI *)(_Out_  PLARGE_INTEGER))GetProcAddress(LoadLibrary("ntdll.dll"), "NtQuerySystemTime");
#endif

	mem = node_alloc((max + 2*EXTRA_SPACE + 64));
	count = max;
	ptr = 0;

#ifdef NO_CYCLE
	for (i = 0; i < 32; i++)
		RTMD_VAL("#init", i);
#else
	for (i = 0; i < EXTRA_SPACE; i++)
		RTMD_InitCycleTime("#cycle");
	for (i = 0; i < 64; i++)
		RTMD_VAL("#cyctst", i);
#endif
}

void RTMD_FlushStorage(const char* filename)
{
	FILE* f;
#ifndef NO_CYCLE
	int i;
	for (i = 0; i < EXTRA_SPACE; i++)
		RTMD_InitCycleTime("#cycleend");
#endif

	f = fopen(filename, "w+b");
	if (f != NULL)
	{
		fwrite(mem, ptr * sizeof(RTMD_Node_t), 1, f);
		fclose(f);
	}
	else
	{
		fprintf(stderr, "RTMD: Can't flush RTMD to %s file!\n", filename);
	}

	node_free(mem);
	ptr = 0;
	count = 0;
	mem = NULL;
}

#ifdef NO_CYCLE
void RTMD_SetInt(const char* name, int clineNumber, int cval)
{
    if (unlikely(mem == NULL))
		return;

	struct timeval tv;
	int err = gettimeofday(&tv, NULL);
    if (unlikely(err)
	{
/*		fprintf(stderr, "RTMD: Can't get time!\n"); */
		return;
	}
	RTMD_SetTime(name, clineNumber, cval, &tv);
}
#endif

void RTMD_SetTime(const char* name, int clineNumber, int cval, const struct timeval *tv)
{
    if (unlikely(mem == NULL))
		return;

    if (ptr < count)
	{
        unsigned slot = INCREMENT_SLOT(ptr);
        if (slot < count)
		{            
			mem[slot].secs = tv->tv_sec;
			mem[slot].usecs = tv->tv_usec;

            FAST_STORE_NAME_1(name, mem[slot].name, RTMD_FLAG_GTOFDAY);

			mem[slot].lineNumber = clineNumber;
			mem[slot].val = cval;

            FAST_STORE_NAME_2(name, mem[slot].name, RTMD_FLAG_GTOFDAY);
		}
	}
}

#ifndef NO_CYCLE
void RTMD_InitCycleTime(const char* name)
{
	struct timeval tv;
	int err = gettimeofday(&tv, NULL);
    if (unlikely(err))
	{
/*		fprintf(stderr, "RTMD: Can't get time!\n"); */
		return;
	}

    if (unlikely(mem == NULL))
		return;

    if (ptr < count + EXTRA_SPACE)
	{
        unsigned slot = INCREMENT_SLOT(ptr);
        if (slot < count + EXTRA_SPACE)
		{
			mem[slot].secs = tv.tv_sec;
			mem[slot].usecs = tv.tv_usec;            
			mem[slot].val64 = get64(getticks());

            FAST_STORE_NAME_1(name, mem[slot].name, RTMD_FLAG_CYCLEINI);
            FAST_STORE_NAME_2(name, mem[slot].name, RTMD_FLAG_CYCLEINI);
		}
	}
}

#ifdef __linux
#define _GNU_SOURCE
#include <unistd.h>
#include <sys/types.h>
#include <sys/syscall.h>

inline void RTMD_SetIntThread(const char*  name, int clineNumber, int cval)
{
    static __thread pid_t stid; // __thread variables can't be initialized (zeroed on clone)
    if (unlikely(stid == 0)) {
        stid = (pid_t) syscall (SYS_gettid);
    }

    int s = -(int)stid;

    RTMD_SetInt(name, s, cval);
}

#endif


void RTMD_SetInt(const char*  name, int clineNumber, int cval)
{
    unsigned l_count = count; //store it to register, otherwise sync* operation will cuase to reread it
    if (ptr < l_count)
    {
        unsigned slot = INCREMENT_SLOT(ptr);
        if (slot < l_count)
        {
            //uint64_t v = get64(getticks());
            mem[slot].tick = get64(getticks());

            FAST_STORE_NAME_1(name, mem[slot].name, RTMD_FLAG_CYCLE);
            //FAST_STORE_NAME_2(name, mem[slot].name, RTMD_FLAG_CYCLE);

            //mem[slot].tick = v;
            //mem[slot].val64 = (uint64_t)cval << 32 | clineNumber;
            mem[slot].lineNumber = clineNumber;
            mem[slot].val = cval;

            FAST_STORE_NAME_2(name, mem[slot].name, RTMD_FLAG_CYCLE);

        }
    }
}
#endif



