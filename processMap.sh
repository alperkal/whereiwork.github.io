#!/bin/bash

MAX_STORY_SIZE=10
STORY_NAME="main"
echo "Processing maps..."
echo "var locations = [	" > assets/js/nodes.js

for post in _posts/*.md; do
     link=$(echo $post|cut -c 19-| cut -d'.' -f1)
     title=$(cat $post|grep "title:"|tail -1 |cut -d' ' -f2-| tr -d '"')
     latitute=$(cat $post|grep "  latitude: "|tail -1 |cut -d' ' -f4)
     longitude=$(cat $post|grep "  longitude: "|tail -1 |cut -d' ' -f4)
     image=$(cat $post|grep "image: "|tail -1 |cut -d' ' -f2)
     echo "['$title', $latitute, $longitude, '$image', '/$link']," >> assets/js/nodes.js
done

echo "];" >> assets/js/nodes.js

echo "Processing Stories..."

echo "---
layout: ampstory
title: whereI.work/today" > _stories/$STORY_NAME.md
COUNTER=0
for post in `ls _posts/*.md | sort -g -r`; do
     let COUNTER=COUNTER+1

     link=$(echo $post|cut -c 19-| cut -d'.' -f1)
     title=$(cat $post|grep "title:"|tail -1 |cut -d' ' -f2-| tr -d '"')
     latitute=$(cat $post|grep "  latitude: "|tail -1 |cut -d' ' -f4)
     longitude=$(cat $post|grep "  longitude: "|tail -1 |cut -d' ' -f4)
     image=$(cat $post|grep "image: "|tail -1 |cut -d' ' -f2)

     if [[ $COUNTER -eq 1 ]]; then
          echo "cover:" >> _stories/$STORY_NAME.md
          echo "  title: <h1>$title</h1>" >> _stories/$STORY_NAME.md
          echo "  background: $image" >> _stories/$STORY_NAME.md
          echo "pages: " >> _stories/$STORY_NAME.md
     else
          echo "- layout: thirds" >> _stories/$STORY_NAME.md
          echo "  top: <h1>$title</h1>" >> _stories/$STORY_NAME.md
          echo "  background: $image" >> _stories/$STORY_NAME.md
     fi

     if [[ $COUNTER -eq $MAX_STORY_SIZE ]]; then
          break
     fi
done

echo "---" >> _stories/$STORY_NAME.md