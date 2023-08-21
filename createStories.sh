#!/bin/bash
STORY_FILE=_stories/main.md
SOURCE=_posts

coverFile=`ls -1 $SOURCE/*.md | tail -1`
image=$(cat "$coverFile"|grep image| cut -d ":" -f 2| cut -c2-| cut -d "/" -f 3)
title=$(cat "$coverFile"|grep title| cut -d ":" -f 2| cut -c3-| rev|cut -c2-| rev)

echo """---
layout: ampstory
title: whereI.work/today
cover:
  title: <h1>$title</h1>
  background: /assets/img/optimised/640/$image""" > $STORY_FILE
echo "pages: " >> $STORY_FILE

counter=0

for f in `ls -1 $SOURCE/*.md`; do
    if [ $f = $coverFile ]; then
        continue;
    fi
    image=$(cat "$f"|grep image| cut -d ":" -f 2| cut -c2-| cut -d "/" -f 3)
    title=$(cat "$f"|grep title| cut -d ":" -f 2| cut -c3-| rev|cut -c2-| rev)
    echo """- layout: thirds
  top: <h1>$title</h1>
  background: /assets/img/optimised/640/$image""" >> $STORY_FILE
  counter=$((counter+1))
  if [ $counter = 10 ]; then
    break;
  fi
done

echo "---" >> $STORY_FILE