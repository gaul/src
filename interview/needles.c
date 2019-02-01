#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

/* Given two strings, remove all characters contained in the latter from
 * the former.  Note that order is preserved.  For example:
 *
 *     "ab",       "b"    -> "a"
 *     "abcdabcd", "acec" -> "bdbd"
 *
 * What is the run-time of your algorithm?  How much memory does it use?  Is it
 * optimal?
 *
 * linear search with memcpy:    O(nh**2)
 * linear search without memcpy: O(nh)
 * sort then binary search:      O(n log n + h log n)
 * table lookup:                 O(n + h)
 */
void remove_needles(char *haystack, const char *needles)
{
    size_t i, j;
    char needles_map[1 << CHAR_BIT] = {0};

    /* build exclusion table */
    for (i = 0; needles[i] != '\0'; ++i) {
        needles_map[(size_t)needles[i]] = 1;
    }

    /* remove chars contained in exclusion table */
    for (i = 0, j = 0; haystack[i] != '\0'; ++i) {
        if (needles_map[(size_t)haystack[i]] == 0) {
            haystack[j++] = haystack[i];
        }
    }

    haystack[j] = '\0';
}

void remove_needles_test(const char *haystack, const char *needles,
                         const char *expected)
{
    char *haystack_mutable = strdup(haystack);
    remove_needles(haystack_mutable, needles);
    assert(strcmp(haystack_mutable, expected) == 0);
}

int main(int argc, char *argv[])
{
    (void)argc;
    (void)argv;
    remove_needles_test("", "", "");
    remove_needles_test("a", "", "a");
    remove_needles_test("", "a", "");
    remove_needles_test("ab", "b", "a");
    remove_needles_test("bab", "b", "a");
    remove_needles_test("bab", "a", "bb");
    remove_needles_test("abcdabcd", "acec", "bdbd");
    return 0;
}
