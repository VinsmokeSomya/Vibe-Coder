#!/bin/bash
# -*- coding: utf-8 -*-

project_dir=$1
shift

# Run the espada script
espada $project_dir "$@"

# Patch the permissions of the generated files to be owned by nobody except prompt file
find "$project_dir" -mindepth 1 -maxdepth 1 ! -path "$project_dir/prompt" -exec chown -R nobody:nogroup {} + -exec chmod -R 777 {} +
