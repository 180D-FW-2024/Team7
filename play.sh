#!/bin/zsh

if [[ "$PWD:t" != "Team7" && "$PWD:t" != "bowling" ]]; then
    echo "Script must be run from within the project directory"
    exit 1
fi

source env/bin/activate

cd main

python main.py

deactivate

