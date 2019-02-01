#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *remove_needles(char *haystack, const char *needles)
{
    char *output = malloc(strlen(haystack) + 1);
    char *ret_output = output;
    char *token;
    while ((token = strtok(haystack, needles)) != NULL) {
        strcpy(output, token);
        output += strlen(token);
        haystack = NULL;
    }
    *output = '\0';
    return ret_output;
}

void remove_needles_test(const char *haystack, const char *needles,
                         const char *expected)
{
    char *haystack_mutable = strdup(haystack);
    char *output = remove_needles(haystack_mutable, needles);
    assert(strcmp(output, expected) == 0);
    free(output);
    free(haystack_mutable);
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
