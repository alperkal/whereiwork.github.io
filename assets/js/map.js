
  // [START maps_overlay_popup]
let map, popup, Popup;


function initialize() {
	var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 3,
          center: new google.maps.LatLng(48.203463, 16.373287),
          mapTypeId: google.maps.MapTypeId.ROADMAP,
	});

	var infowindow = new google.maps.InfoWindow();
	var marker, i;

	for (i = 0; i < locations.length; i++) {  
	    marker = new google.maps.Marker({
    	    position: new google.maps.LatLng(locations[i][1], locations[i][2]),
			map: map
		});

		google.maps.event.addListener(marker, 'click', (function(marker, i) {
			return function() {
				var content='<a href="'+locations[i][4]+'">'+locations[i][0]+'</a>'+'<br><img src="'+locations[i][3]+'" style="width:300px;">';
				infowindow.setContent(content);
				infowindow.open(map, marker);
			}
		})(marker, i));
	}
}