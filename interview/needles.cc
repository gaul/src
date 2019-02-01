#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <string>
#include <unordered_set>

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
void remove_needles(std::string &haystack, const std::string &needles)
{
    std::unordered_set<char> needles_set(needles.begin(), needles.end());
    std::string::iterator haystack_it = haystack.begin();
    for (char c : haystack) {
        if (needles_set.find(c) == needles_set.end()) {
            *haystack_it++ = c;
        }
    }
    haystack.erase(haystack_it, haystack.end());
}

void remove_needles_test(std::string haystack, const std::string &needles,
                         const std::string &expected)
{
    remove_needles(haystack, needles);
    if (haystack != expected) {
        std::cout << "expected: " << expected
                  << " actual: " << haystack << std::endl;
        std::exit(1);
    }
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
