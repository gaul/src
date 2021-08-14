/*
 * Measure overhead of gettimeofday:
 *
 * Intel NUC 8:     33 us for 1000 iterations
 * Raspberry Pi 4: 401 us for 1000 iterations
 */

#include <stdio.h>
#include <sys/time.h>
#include <time.h>

#define LEN 1000

int main(int argc, char *argv[])
{
	int res;
	size_t i;
	struct timeval tv[LEN];
	struct timespec ts[LEN];

	for (i = 0; i < LEN; ++i) {
		res = gettimeofday(&tv[i], NULL);
		if (res != 0) {
			perror("gettimeofday");
			return 1;
		}
	}
	printf("gettimeofday:\n");
	printf("start: %ld.%06ld\n", tv[0].tv_sec,       tv[0].tv_usec);
	printf("end:   %ld.%06ld\n", tv[LEN - 1].tv_sec, tv[LEN - 1].tv_usec);

	for (i = 0; i < LEN; ++i) {
		res = clock_gettime(CLOCK_MONOTONIC, &ts[i]);
		if (res != 0) {
			perror("clock_gettime");
			return 1;
		}
	}
	printf("clock_gettime(CLOCK_MONOTONIC):\n");
	printf("start: %ld.%09ld\n", ts[0].tv_sec,       ts[0].tv_nsec);
	printf("end:   %ld.%09ld\n", ts[LEN - 1].tv_sec, ts[LEN - 1].tv_nsec);

	return 0;
}
