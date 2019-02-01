#!/bin/sh

remove_needles() {
    echo -n "$1" | tr -d "$2"
}

remove_needles_test() {
    output=`remove_needles "$1" "$2"`
    if [ "$output" != "$3" ]; then
        echo "fail: '$1' '$2' '$3' != '$output'"
        exit 1
    fi
}

remove_needles_test '' '' ''
remove_needles_test 'a' '' 'a'
remove_needles_test '' 'a' ''
remove_needles_test 'ab' 'b' 'a'
remove_needles_test 'bab' 'b' 'a'
remove_needles_test 'bab' 'a' 'bb'
remove_needles_test 'abcdabcd' 'acec' 'bdbd'
