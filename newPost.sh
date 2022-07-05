#!/bin/bash

filename=$1
title=$2
#  Resize image

convert -resize x1000 $filename $filename

date=`exiftool -s -s -s -d "%Y-%m-%d" -DateTimeOriginal -S $filename`

shortFileName=${filename##*/}
fileExtension="${filename##*.}"
fileNameWithoutExtension="${filename%.*}"
name="${shortFileName%.jpg}"

echo "$date-$name"

# GPS Coordinates:

longitude=`exiftool -s -s -s -gpslongitude $filename -n`
latitude=`exiftool -s -s -s -gpslatitude $filename -n`
echo "---
layout: post
title: \"$title\"
author: \"Alper Kalaycioglu\"
categories: whereiwork
tags: [documentation]
image: assets/img/$name.jpg
amp: true
location:
  latitude: $latitude
  longitude: $longitude
---" > _posts/$date-$name.md


echo "---
layout: amp
title: \"$title\"
author: \"Alper Kalaycioglu\"
categories: whereiwork
tags: [documentation]
image: $name.jpg
location:
  latitude: $latitude
  longitude: $longitude
---" > _amp/$date-$name.md

./processMap.sh
./bash-responsive-images.sh
./createStories.sh