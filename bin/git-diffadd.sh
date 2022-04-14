#!/usr/bin/env bash

#
# First check if some files was added to commit, but then updated
# this looks like "MM" or "AM"
#
# If no files was added look for mofified files "M"
# NOTE: the same picture will be appeared when all files added to commit
#       so, use git status first and don't run this tool if no files available for diff
#
# @see also https://stackoverflow.com/questions/44448087/reference-for-git-status-shorthand
#

modified=`git status --porcelain "$@" | grep '^\s*\SM\s' | awk '{ print $2 }'`

[[ "$modified" == "" ]] && modified=`git status --porcelain "$@" | grep '^\s*M\s' | awk '{ print $2 }'`

for file in $modified; do
  git difftool -y $file
  read -r -p "$file: Add to commit? [Y/n] " ans

  [[ "$ans" != [nN] ]] && git add $file
done
