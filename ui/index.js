
$(document).ready(function () {
    getMapathons();
});


function getMapathons() {
    return $.getJSON("http://localhost:5000/mapathon/list", handleMapathonsData);
}   

function handleMapathonsData(data) {
    console.log(data);
    data.forEach(item => {
        // TODO much better list
        $("#mapathonList").append('<li class="list-group-item">Mapathon held on ' +
            item.mapathon_info.mapathon_date + ' at ' +
            item.mapathon_info.mapathon_time_utc + ' for project ' +
            item.mapathon_info.project_number +
            '</li>');
    });
}