
$(document).ready(function () {
    getMapathons();
});


function getMapathons() {
    return $.getJSON("http://localhost:5000/mapathon/list", handleMapathonsData);
}   

function handleMapathonsData(data) {
    console.log(data);
    data.forEach(item => {
        var html = '<div class="card"><div class="card-body"><h5 class="card-title">' + item.mapathon_info.mapathon_title + '</h5>' +
            '<p class="card-text">Mapathon held on ' +
            item.mapathon_info.mapathon_date + ' at ' +
            item.mapathon_info.mapathon_time_utc + ' (UTC) for project ' +
            '<a target="_blank" href="https://tasks.hotosm.org/project/' + item.mapathon_info.project_number + '">' + item.mapathon_info.project_number + '</a>. ' +
            item.mapathon_users.length + ' <i class="fa fa-user" aria-hidden="true"></i></p>' +
            '<a href="#" class="btn btn-primary">Statistics</a></div></div>';
        $("#mapathonList").append(html);
    });
}
