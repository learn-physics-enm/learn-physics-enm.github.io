#!/bin/bash

echo -e "\e[42mLearn Physics ENM Website (Node.js & Docusaurus) container is active.\e[0m"

echo -n "(b)uild or (s)tart website? "
read input

if [[ "$input" == "b" ]]; then
    npm run build
elif [[ "$input" == "s" ]]; then
    npm run start
else
    echo "Invalid option selected. Doing nothing."
fi