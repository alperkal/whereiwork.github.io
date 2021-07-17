#!/bin/bash

filename=$1
title=$2
#  Resize image

sips -Z 1000 $filename

date=`exiftool -s -s -s -d "%Y-%m-%e" -DateTimeOriginal -S $filename`

shortFileName=${filename##*/}
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
image: $name.jpg
location:
  latitude: $latitude
  longitude: $longitude
---" > _posts/$date-$name.md