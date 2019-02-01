#!/usr/bin/env python

# find useless C and C++ standard #includes via simple string search.

# XXX using namespace std
# XXX using std::string
# XXX std::bind1st and std::mem_fun
# XXX iosfwd
# XXX math
# XXX boost using directive
# XXX needs unit tests

import sys

__VERSION__ = 20120329

# XXX where did I source these from?
CXX_HEADERS = {
    'algorithm' : [
            'accumulate', 'adjacent_difference', 'adjacent_find',
            'binary_search', 'copy', 'copy_backward', 'count', 'count_if',
            'equal', 'equal_range', 'fill', 'fill_n', 'find', 'find_end',
            'find_first_of', 'find_if', 'for_each', 'generate', 'generate_n',
            'includes', 'inner_product', 'inplace_merge', 'is_heap',
            'iter_swap', 'lexicographical_compare', 'lower_bound', 'make_heap',
            'max', 'max_element', 'merge', 'min', 'min_element', 'mismatch',
            'next_permutation', 'nth_element', 'partial_sort',
            'partial_sort_copy', 'partial_sum', 'partition', 'pop_heap',
            'prev_permutation', 'push_heap', 'random_shuffle', 'remove',
            'remove_copy', 'remove_copy_if', 'remove_if', 'replace',
            'replace_copy', 'replace_copy_if', 'replace_if', 'reverse',
            'reverse_copy', 'rotate', 'rotate_copy', 'search', 'search_n',
            'set_difference', 'set_intersection', 'set_symmetric_difference',
            'set_union', 'sort', 'sort_heap', 'stable_partition', 'stable_sort',
            'swap', 'swap_ranges', 'transform', 'unique', 'unique_copy',
            'upper_bound', ],
    'fstream'  : [ 'ifstream', 'ofstream', ],
    #'iosfwd'   : [ 'ostream', 'istream', ],
    'iostream' : [ 'cerr', 'cin', 'cout', ],
    'list'     : [ 'list', ],
    #'iterator' : [],
    'map'      : [ 'map', 'multimap', ],
    'queue'    : [ 'deque', 'priority_queue', 'queue', ],
    'set'      : [ 'multiset', 'set', ],
    'sstream'  : [ 'istringstream', 'ostringstream', 'stringstream', ],
    'stack'    : [ 'stack', ],
    'string'   : [ 'string', 'wstring', ],
    'tr1/functional' : [ 'bind', 'function', 'mem_fn', 'result_of', ],
    'utility'  : [ 'make_pair', 'pair', ],
    'vector'   : [ 'vector', ],
}

C_HEADERS = {
    'cctype' : [
            'isalnum', 'isalpha', 'iscntrl', 'isdigit', 'isgraph', 'islower',
            'isprint', 'ispunct', 'isspace', 'isupper', 'isxdigit', 'tolower',
            'toupper', ],
    'cerrno' : [ 'errno', 'clearerr', 'feof', 'ferror', 'perror', ],
    'cmath' : [
            'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
            'div', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'labs', 'ldexp',
            'ldiv', 'log', 'log10', 'modf', 'pow', 'sin', 'sinh', 'sqrt',
            'tan', 'tanh', ],
    'cstddef' : [ 'NULL', 'ptrdiff_t', 'size_t', ],
    'cstdio' : [
            'clearerr', 'fclose', 'feof', 'ferror', 'fflush', 'fgetc',
            'fgetpos', 'fgets', 'FILE', 'fopen', 'fprintf', 'fputc', 'fputs',
            'fread', 'freopen', 'fscanf', 'fseek', 'fsetpos', 'ftell', 'fwrite',
            'getc', 'getchar', 'gets', 'perror', 'printf', 'putc', 'putchar',
            'puts', 'remove', 'rename', 'rewind', 'scanf', 'setbuf', 'setvbuf',
            'snprintf', 'sprintf', 'sscanf', 'tmpfile', 'tmpnam', 'ungetc',
            'vprintf', 'vfprintf', 'vsprintf', 'vscanf', 'vfscanf', 'vsscanf',
            ],
    'cstdlib' : [
            'abort', 'abs', 'atexit', 'atof', 'atoi', 'atol', 'bsearch',
            'calloc', 'div', 'exit', 'free', 'getenv', 'labs', 'ldiv', 'malloc',
            'qsort', 'rand', 'realloc', 'srand', 'strtod', 'strtol', 'strtoul',
            'system', ],
    'cstring' : [
            'memchr', 'memcmp', 'memcpy', 'memmove', 'memset', 'strcat',
            'strchr', 'strcmp', 'strcoll', 'strcpy', 'strcspn', 'strerror',
            'strlen', 'strncat', 'strncmp', 'strncpy', 'strpbrk', 'strrchr',
            'strspn', 'strstr', 'strtok', 'strxfrm', ],
    'ctime' : [
            'asctime', 'clock', 'ctime', 'difftime', 'gmtime', 'localtime',
            'mktime', 'strftime', 'time', ],
}

# GNU extensions
C_HEADERS['cstring'] += [ 'strdup', ]

for cxx_header in C_HEADERS.keys():
    c_header = cxx_header[1:] + '.h'
    C_HEADERS[c_header] = C_HEADERS[cxx_header]

BOOST_HEADERS = {
    'boost/bind.hpp' :              [ 'bind' ],
    #'boost/foreach.hpp' :           [ 'BOOST_FOREACH' ],
    'boost/format.hpp' :            [ 'format' ],
    'boost/function.hpp' :          [ 'function' ],
    'boost/make_shared.hpp' :       [ 'allocate_shared', 'make_shared', ],
    'boost/scoped_ptr.hpp' :        [ 'scoped_ptr' ],
    'boost/shared_mutex.hpp' :      [ 'shared_mutex', ],
    'boost/shared_ptr.hpp' :        [ 'shared_ptr' ],
    #'boost/thread.hpp' :            [],  # meta header?
    'boost/unordered_map.hpp' :     [ 'unordered_map' ],
    'boost/thread/condition_variable.hpp' :
            [ 'condition_variable', ],
    'boost/thread/mutex.hpp' :      [ 'mutex' ],  # TODO: shared_mutex?
    'boost/utility/enable_if.hpp' : [ 'disable_if', 'enable_if', ],
}

ALL_HEADERS = {}
#ALL_HEADERS.update(C_HEADERS)
ALL_HEADERS.update(CXX_HEADERS)
#ALL_HEADERS.update(BOOST_HEADERS)

# TODO: needs to deal with situations like #include <set>  struct tset;
def find_string_in_file(filename, match_string, exclude_strings = []):
    with file(filename) as f:
        for line in f:
            if match_string not in line:
                continue
            # now we have matched
            found = False
            for exclude_string in exclude_strings:
                if exclude_string in line:
                    found = True
            if not found:
                return True
    return False

def main():
    # TODO: this should take file names from stdin
    from os import popen
    exit_code = 0
    FIND_CMD = 'find -name \*.h -o -name \*.c -o -name \*.cc -o -name \*.cpp'
    #FIND_CMD = 'find -name \*.h'
    for filename in popen(FIND_CMD):
        filename = filename.rstrip()
        for include, containers in ALL_HEADERS.iteritems():
            if not find_string_in_file(filename, '#include <%s>' % include):
                continue
            using_namespace_std = find_string_in_file(
                    filename, 'using namespace std;')
            found = False
            for container in containers:
                # XXX this is tricky since C functions are global namespace
                needle = container
                #needle = 'std::' + container
                #needle = 'boost::' + container
                using_container = find_string_in_file(
                        filename, 'using %s;' % needle)
                if using_namespace_std or using_container:
                    needle = container
                if find_string_in_file(filename, needle,
                        ['#include <%s>' % include, 'using %s' % needle]):
                    found = True
                    break
            if not found:
                print filename, include
                exit_code = 1
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
