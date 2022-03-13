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

ampFilename=${fileNameWithoutExtension}_amp.${fileExtension}
echo "ampFilename: $ampFilename"
convert -resize x600 $filename $ampFilename

echo "$date-$name"

# GPS Coordinates:

longitude=`exiftool -s -s -s -gpslongitude $filename -n`
latitude=`exiftool -s -s -s -gpslatitude $filename -n`
ampImageName=`basename $ampFilename`
echo "---
layout: post
title: \"$title\"
author: \"Alper Kalaycioglu\"
categories: whereiwork
tags: [documentation]
image: $name.jpg
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
image: $ampImageName
location:
  latitude: $latitude
  longitude: $longitude
---" > _amp/$date-$name.md

./processMap.sh