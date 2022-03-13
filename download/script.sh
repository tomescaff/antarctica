#!/bin/sh

# file with the url of meteorological data
input="url.txt"

# read the input and download data
# [[ -n "$line" ]] handles lines with no \n character
while IFS= read -r line || [[ -n "$line" ]]
do
    echo "donwloading files from: $line"
    wget -r -np -nH --cut-dirs=3 -A txt -P data "$line"
done < $input

