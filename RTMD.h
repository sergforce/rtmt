/*
 * RTMD.h
 *
 *  Created on: Oct 18, 2010
 *      Author: serg
 */

#ifndef RTMD_H_
#define RTMD_H_

#ifdef __cplusplus
extern "C" {
#endif
/*
 * Library prototypes
 */

#if defined WITH_RTMD && !defined NO_RTMD

void RTMD_InitStorage(unsigned max);
void RTMD_FlushStorage(const char* filename);

void RTMD_SetInt(const char* name, int lineNumber, int val);
void RTMD_SetTime(const char* name, int lineNumber, int val, const struct timeval *tv);

/* Cycle extension */
void RTMD_SetCycleTime(const char* name, int lineNumber, int val);
void RTMD_InitCycleTime(const char* name);

void RTMD_SetIntThread(const char*  name, int clineNumber, int cval);

int RTMD_IsFull(void);

# define RTMD_VAL(a, v)        RTMD_SetInt((a), __LINE__, (v))
# define RTMD_SET(a)           RTMD_SetInt((a), __LINE__, 1)
# define RTMD_CLEAR(a)         RTMD_SetInt((a), __LINE__, 0)
# define RTMD_PULSE(a)         ( RTMD_SET(a), RTMD_CLEAR(a))

# define RTMD_TH_NAME(a)       RTMD_SetThreadName(a)
# define RTMD_TH_VAL(a, v)     RTMD_SetIntThread((a), __LINE__, (v))
# define RTMD_TH_SET(a)        RTMD_SetIntThread((a), __LINE__, 1)
# define RTMD_TH_CLEAR(a)      RTMD_SetIntThread((a), __LINE__, 0)
# define RTMD_TH_PULSE(a)      ( RTMD_TH_SET(a), RTMD_TH_CLEAR(a))

# define RTMD_INIT(x)             RTMD_InitStorage((x))
# define RTMD_FLUSH(x)            RTMD_FlushStorage((x))
# define RTMD_SETTIME(a, tv)      RTMD_SetTime((a), __LINE__, 1, tv);
# define RTMD_CLEARTIME(a, tv)    RTMD_SetTime((a), __LINE__, 0, tv);
# define RTMD_FULL	              RTMD_IsFull
#else
# define RTMD_VAL(a, v)
# define RTMD_SET(a)
# define RTMD_CLEAR(a)
# define RTMD_PULSE(a)

# define RTMD_TH_NAME(a)
# define RTMD_TH_VAL(a, v)
# define RTMD_TH_SET(a)
# define RTMD_TH_CLEAR(a)
# define RTMD_TH_PULSE(a)

# define RTMD_INIT(x)
# define RTMD_FLUSH(x)
# define RTMD_SETTIME(a, tv) 
# define RTMD_CLEARTIME(a, tv) 
# define RTMD_FULL
#endif

#ifdef __cplusplus
}
#endif

#endif /* RTMD_H_ */
