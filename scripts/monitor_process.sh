#!/usr/bin/env bash

while true; do
    clear

    echo "===== GitHub Activity Script Monitor ====="
    echo

    echo "Running gh processes:"
    ps -o pid,etime,cmd -C gh

    echo
    echo "GraphQL batches completed:"
    if [ -d graphql-batches ]; then
        ls graphql-batches | wc -l
    else
        echo 0
    fi

    echo
    echo "Output file sizes:"
    ls -lh active-following.txt inactive-following.txt all-results.txt following-activity.csv 2>/dev/null

    echo
    echo "Line counts:"
    wc -l active-following.txt inactive-following.txt all-results.txt 2>/dev/null

    echo
    echo "Timestamp:"
    date

    sleep 5
done
