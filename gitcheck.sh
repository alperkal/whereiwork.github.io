#!/bin/bash
echo "First Param: $1"
echo "Second Param: $2"

filename=$1
if [ -z "$filename" ]
then
    filename=`git diff --name-only HEAD^|head -1`
fi

commitMessage=$2
if [ -z "$commitMessage" ]
then
    commitMessage=`git log -1 --pretty=format:%B`
fi


if [[ $filename == assets/img/* ]] && ([[ $filename == *jpg ]] || [[ $filename == *JPG ]]) ; then
    echo "True $commitMessage"
    ./newPost.sh $filename "$commitMessage"
else
    echo "false"
fi