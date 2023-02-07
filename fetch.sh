#!/bin/bash

set -e
set -x

mkdir v8
cd v8

gclient root

gclient config --spec "solutions = [
  {
    \"name\": \"src\",
    \"url\": \"git@github.com:tkm-ce/v8-yg.git\",
    \"managed\": False,
    \"custom_deps\": {},
    \"custom_vars\": {},
  },
]
"

gclient sync --nohooks --no-history

echo 'I had clone the repo without history. In order to fetch other branch you have to unshallow it till they exist.'
