#!/bin/bash

echo "var locations = [	" > assets/js/nodes.js

for post in _posts/*.md; do
     link=$(echo ${post##*-}| cut -d'.' -f1)
     title=$(cat $post|grep "title:"|tail -1 |cut -d' ' -f2-| tr -d '"')
     latitute=$(cat $post|grep "  latitude: "|tail -1 |cut -d' ' -f4)
     longitude=$(cat $post|grep "  longitude: "|tail -1 |cut -d' ' -f4)
     image=$(cat $post|grep "image: "|tail -1 |cut -d' ' -f2)
     echo "['$title', $latitute, $longitude, '/assets/img/$image', '/$link']," >> assets/js/nodes.js
done

echo "];" >> assets/js/nodes.js
