#include <stdint.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


#define WITH_RTMD
#include <RTMD.h>

pthread_mutex_t g_mutex = PTHREAD_MUTEX_INITIALIZER;

int g_value = 0;

volatile int g_lock = 1;

void* thread_adder(void* param)
{
    int max = (intptr_t)param;
    int i;

    while(g_lock);

    for (i = 0; i < max; i++) {
        RTMD_TH_SET("add_lock");
        pthread_mutex_lock(&g_mutex);
        ++g_value;
        pthread_mutex_unlock(&g_mutex);
        RTMD_TH_CLEAR("add_lock");
    }
    return NULL;
}

void* thread_remover(void* param)
{
    int max = (intptr_t)param;
    int i;

    while(g_lock);

    for (i = 0; i < max; i++) {
        RTMD_TH_SET("rem_lock");
        pthread_mutex_lock(&g_mutex);
        --g_value;
        pthread_mutex_unlock(&g_mutex);
        RTMD_TH_CLEAR("rem_lock");
    }
    return NULL;
}

#define MAX_THREADS     128

int main(int argc, char** argv)
{
    int opt;
    int adders = 1;
    int removers = 1;
    int iterations = 10000;

    while ((opt = getopt(argc, argv, "a:r:i:")) != -1) {
        switch (opt) {
        case 'a':
            adders =  atoi(optarg);
            break;
        case 'r':
            removers = atoi(optarg);
            break;
        case 'i':
            iterations = atoi(optarg);
            break;
        default: /* '?' */
            fprintf(stderr, "Usage: %s [-a adder_threads] [-r remover_threads] [-i iterations]\n",
                    argv[0]);
            exit(EXIT_FAILURE);
        }
    }

    RTMD_INIT(iterations * 2 * (adders + removers) + 10000);

    pthread_t padders[MAX_THREADS];
    pthread_t premovers[MAX_THREADS];
    int i;

    for (i = 0; i < adders; i++) {
        pthread_create(&padders[i], NULL, thread_adder, (void*)(intptr_t)iterations);
    }
    for (i = 0; i < removers; i++) {
        pthread_create(&premovers[i], NULL, thread_remover, (void*)(intptr_t)iterations);
    }

    g_lock = 0; //Unlock threads

    for (i = 0; i < adders; i++) {
        pthread_join(padders[i], NULL);
    }
    for (i = 0; i < removers; i++) {
        pthread_join(premovers[i], NULL);
    }

    RTMD_FLUSH("test_mutex_data.rtmd");
    return 0;
}
