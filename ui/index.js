
var projects = [];
var projectNumberAwesomplete = null;
var projectSelectedNumber = null;

var serverURL = "http://localhost:5000";


$(document).ready(function () {
    getMapathons();

    getProjectSearchPage(1);

    $("#createStatisticsForm").submit(createStatistics);
});

//
// Functions for listing and showing existing mapathon statistics
//

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
            '<a href="#" id="' + item._id.$oid + '" class="btn btn-primary">Show statistics page</a></div></div>';
        $("#mapathonList").append(html);

        $("#" + item._id.$oid).on('click', showMapathon);
    });
}

function showMapathon(event) {
    // TODO use event.target.id to show mapathon statistics page
    console.log(event);
}

//
// Functions for creating mapathon statistics
//

function createStatistics(event) {
    event.preventDefault();
    hideAlerts();
    $("#serverSuccessAlert").text("Sending the data...");
    $("#serverSuccessAlert").show();
    var method = "/stats/create";
    $.ajax({
        type: 'POST',
        url: serverURL + method,
        data: $("#createStatisticsForm").serialize(),
        timeout: 10000,
        success: function (data) {
            console.log(data);
            hideAlerts();
            if (data.status == 'OK') {
                $("#serverSuccessAlert").text("Processing the data...");
                $("#serverSuccessAlert").show();

                setTimeout(updateStatsCreationState, 5000, data.stat_task_uuid);
            }
            else {
                $("#serverErrorAlert").text("Error on starting processing the data");
                $("#serverErrorAlert").show();
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
            hideAlerts();
            if (jqXHR.readyState == 0) {
                $("#serverErrorAlert").text("Error connecting the server.");
            }
            else if (jqXHR.status >= 500 && jqXHR.status < 600) {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (server) problem.");
            }
            else if (jqXHR.status >=  400 && jqXHR.status < 500) {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (client) problem.");
            }
            else {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the problem.");
            }
            $("#serverErrorAlert").show();
        }
    });
}

function updateStatsCreationState(stat_task_uuid) {

    var method = "/stats/state"

    var params = {
        stat_task_uuid: stat_task_uuid
    }

    $.ajax({
        type: 'GET',
        url: serverURL + method,
        data: params,
        timeout: 10000,
        success: function (data) {
            console.log(data);
            hideAlerts();
            if (data.state != null) {
                switch (data.state.name) {
                    case "initialized":
                        $("#serverSuccessAlert").text("Processing the data...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "getting_project_data":
                        $("#serverSuccessAlert").text("Getting the project data...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "finding_project_countries":
                        $("#serverSuccessAlert").text("Finding the project country or countries...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "finding_geofabrik_areas":
                        $("#serverSuccessAlert").text("Finding the project areas...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_mapathon_changes":
                        $("#serverSuccessAlert").text("Extracting mapathon changes... Done " + data.state.state_progress + "%");
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_users_list":
                        $("#serverSuccessAlert").text("Finding users who made changes for the mapathon area during the mapathon...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "storing_osm_changes":
                        $("#serverSuccessAlert").text("Storing mapathon changes and usernames...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_statistics_web_page":
                        $("#serverSuccessAlert").text("Creating a web page that visualizes the mapathon statistics...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "storing_to_page_list":
                        // TODO show a link to the user where the statistics page is located
                        $("#serverSuccessAlert").text("Page created and can be found at the...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "error":
                        // TODO more specific errors
                        $("#serverErrorAlert").text("An error happened during statics creation... You can try later again / let Erno Mäkinen, ernoma (at) gmail.com know about the problem.");
                        $("#serverErrorAlert").show();
                        break;
                    default:
                        // Should not be possible to end here
                        $("#serverErrorAlert").text("Server is in state " + data.state + " that is not recognized... Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (server) problem.");
                        $("#serverErrorAlert").show();
                        console.log("unknown state: " + data.state);
                }
                // TODO only set timeout if the statistics creation is not finished
                setTimeout(updateStatsCreationState, 5000, stat_task_uuid);
            }
            else {
                // TODO should maybe just take care of the security issues.
                $("#serverErrorAlert").text("The statistics creation task cannot be found.");
                $("#serverErrorAlert").show();
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
            hideAlerts();
            if (jqXHR.readyState == 0) {
                $("#serverErrorAlert").text("Error connecting the server.");
            }
            else if (jqXHR.status >= 500 && jqXHR.status < 600) {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (server) problem.");
            }
            else if (jqXHR.status >=  400 && jqXHR.status < 500) {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (client) problem.");
            }
            else {
                $("#serverErrorAlert").text("Error happened. Please, let Erno Mäkinen, ernoma (at) gmail.com know about the problem.");
            }
            $("#serverErrorAlert").show();
        }
    });

}

function hideAlerts() {
    $("#serverSuccessAlert").hide();
    $("#serverErrorAlert").hide();
}

function getProjectSearchPage(page) {

    var params = {
        page: page
    };

    $.getJSON("https://tasks.hotosm.org/api/v1/project/search", params, function (data) {
        projects = projects.concat(data.results);
        //console.log(data);
        //console.log(projects);

        var input = document.getElementById("projectNumber");

        var awesompleteList = [];

        for (var i = 0; i < projects.length; i++) {
            var awesompleteItem = {
                label: "#" + projects[i].projectId + " - " + projects[i].name,
                value: projects[i].projectId
            };
            awesompleteList.push(awesompleteItem);
        }

        if (projectNumberAwesomplete != null) {
            projectNumberAwesomplete.list = awesompleteList;
        }
        else {
            projectNumberAwesomplete = new Awesomplete(input, {
                list: awesompleteList,
                minChars: 1,
            });
        }

        Awesomplete.$('#projectNumber').addEventListener("awesomplete-selectcomplete", function() {
            projectSelectedNumber = $('#projectNumber').val();
            projectNumberAwesomplete.close();
        });
        Awesomplete.$('#projectNumber').addEventListener("awesomplete-open", function () {
            if (projectSelectedNumber == $('#projectNumber').val()) {
                projectNumberAwesomplete.close(); // This is because if user has not changed selection
                                                  // it is just distracting to show the list...
            }
        });

        if (data.pagination.hasNext) {

            var nextPage = data.pagination.nextNum;

            setTimeout(function() {
                getProjectSearchPage(nextPage);
            }, 100);
        }
    });
}
