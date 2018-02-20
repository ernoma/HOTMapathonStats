
$(document).ready(function () {
    getMapathons();
});


function getMapathons() {
    return $.getJSON("http://localhost:5000/mapathon/list", handleMapathonsData);
}   

function handleMapathonsData(data) {
	console.log(data);
}