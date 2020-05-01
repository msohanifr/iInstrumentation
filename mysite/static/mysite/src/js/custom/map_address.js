// <img src="directions-icon.png" onclick="mapsSelector('22 dixon dr, florhampark')" />
function mapsSelector(addr) {
    if /* if we're on iOS, open in Apple Maps */
    ((navigator.platform.indexOf("iPhone") != -1) ||
        (navigator.platform.indexOf("iPad") != -1) ||
        (navigator.platform.indexOf("iPod") != -1))
        window.open("maps://maps.google.com/maps?daddr="+addr);
    else /* else use Google */
        window.open("https://maps.google.com/maps?daddr="+addr);
}