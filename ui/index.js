
var projects = [];
var projectNumberAwesomplete = null;
var projectSelectedNumber = null;

var submittedHOTOSMFormData = null;


$(document).ready(function () {

    serverURL = "http://" + window.location.hostname + ":5000";

    getMapathons();

    getProjectSearchPage(1);

    $("#createStatisticsForm").submit(createStatistics);
});

//
// Functions for listing and showing existing mapathon statistics
//

function getMapathons() {
    return $.getJSON(serverURL + "/mapathon/list", handleMapathonsData);
}

function handleMapathonsData(data) {
    //console.log(data);
    data.forEach(item => {
        var html = '<div class="card"><div class="card-body"><h5 class="card-title">' + item.mapathon_info.mapathon_title + '</h5>' +
            '<p class="card-text">Mapathon held on ' +
            item.mapathon_info.mapathon_date + ' at ' +
            item.mapathon_info.mapathon_time_utc + ' (UTC) for project ' +
            '<a target="_blank" href="https://tasks.hotosm.org/project/' + item.mapathon_info.project_number + '">' + item.mapathon_info.project_number + '</a>.</p>' +
            // item.mapathon_users.length + ' <i class="fa fa-user" aria-hidden="true"></i></p>' +
            '<p><a target="_blank" href="stats?' +
            createMapathonStatPageQueryParamsForItem(item);
        html += '&id=' + item._id.$oid;
        html +=
            '" id="' + item._id.$oid + '" class="btn btn-primary">Show statistics page</a></p></div></div>';
        $("#mapathonList").append(html);

        $("#" + item._id.$oid).on('click', showMapathon);
    });
}

function showMapathon(event) {
    // TODO use event.target.id to show mapathon statistics page
    //console.log(event);
}

//
// Functions for creating mapathon statistics
//

function createStatistics(event) {
    event.preventDefault();
    hideAlerts();

    submittedHOTOSMFormData = $("#createStatisticsForm").serializeArray();
    //console.log(submittedHOTOSMFormData);

    if (!checkFormDataGiven(submittedHOTOSMFormData)) {
        $("#serverErrorAlert").text("Please, fill the form fully.");
        $("#serverErrorAlert").show();
        return;
    }

    $("#serverSuccessAlert").text("Sending the data...");
    $("#serverSuccessAlert").show();
    var method = "/stats/create";
    
    // createMapathonStatPageQueryParamsFromFormData(submittedHOTOSMFormData);
    // return;

    // TODO clear updateStatsCreationState timeout if any

    $.ajax({
        type: 'POST',
        url: serverURL + method,
        data: $("#createStatisticsForm").serialize(),
        timeout: 10000,
        success: function (data) {
            //console.log(data);
            hideAlerts();
            $("#serverSuccessAlert").html("Processing the data...");
            $("#serverSuccessAlert").show();

            setTimeout(updateStatsCreationState, 5000, data.stat_task_uuid);
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

function getStatsURLCopyInfo(stat_task_uuid) {
    return "Provided that the statistics are created succesfully, you can find the result page later on the created mapathon statistics list and at the address<br>" +
        "<input type='text' size='40' id='spanStatsURL' value='" +
        window.location.href + "stats?" + 
        createMapathonStatPageQueryParamsFromFormData(submittedHOTOSMFormData) + 
        "&uid=" + stat_task_uuid +
        "'>&nbsp<button class='btn btn-primary' onclick='text=document.getElementById(\"spanStatsURL\").select();document.execCommand(\"copy\");'>Copy</button>" +
        "<br>You can safely close this page now."
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
            //console.log(data);
            hideAlerts();
            if (data.state != null) {
                switch (data.state.name) {
                    case "initialized":
                        $("#serverSuccessAlert").html(
                            "Processing the data...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "getting_project_data":
                        $("#serverSuccessAlert").html(
                            "Getting the project data...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "finding_project_countries":
                        $("#serverSuccessAlert").html(
                            "Finding the project country or countries...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "finding_geofabrik_areas":
                        $("#serverSuccessAlert").html(
                            "Finding the project areas...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_mapathon_changes":
                        $("#serverSuccessAlert").html(
                            "Extracting mapathon changes...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_users_list":
                        $("#serverSuccessAlert").text("Finding users who made changes for the mapathon area during the mapathon...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "storing_osm_changes":
                        $("#serverSuccessAlert").text(
                            "Storing mapathon changes...<br>" +
                            getStatsURLCopyInfo(stat_task_uuid)
                        );
                        $("#serverSuccessAlert").show();
                        break;
                    case "creating_statistics_web_page":
                        $("#serverSuccessAlert").text("Creating a web page that visualizes the mapathon statistics...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "storing_to_page_list":
                        // show a link to the user where the statistics page is located
                        $("#serverSuccessAlert").html(
                            "<a href='" +
                            window.location.href + "stats?" + 
                            createMapathonStatPageQueryParamsFromFormData(submittedHOTOSMFormData) + 
                            "&uid=" + stat_task_uuid + "'>Result page</a> created"
                        );
                        //$("#serverSuccessAlert").text("Page created and can be found at the...");
                        $("#serverSuccessAlert").show();
                        break;
                    case "error":
                        // TODO more specific errors
                        $("#serverErrorAlert").text("An error happened during statistics creation... You can try later again / let Erno Mäkinen, ernoma (at) gmail.com know about the problem.");
                        $("#serverErrorAlert").show();
                        break;
                    default:
                        // Should not be possible to end here
                        $("#serverErrorAlert").text("Server is in state " + data.state + " that is not recognized... Please, let Erno Mäkinen, ernoma (at) gmail.com know about the (server) problem.");
                        $("#serverErrorAlert").show();
                        console.log("unknown state: " + data.state);
                }
                // only set timeout if the statistics creation is not finished
                if (data.state.name != "storing_to_page_list" && data.state.name != "error") {
                    setTimeout(updateStatsCreationState, 5000, stat_task_uuid);
                }
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

function createMapathonStatPageQueryParamsForItem(item) {
    var html = "";
    html += 'title=' + encodeURIComponent(item.mapathon_info.mapathon_title) +
    '&date=' + item.mapathon_info.mapathon_date +
    '&time=' + item.mapathon_info.mapathon_time_utc +
    '&project=' + item.mapathon_info.project_number +
    '&types=';
    item.mapathon_info.types_of_mapping.forEach(type => {
        html += type + ','
    });
    html = html.slice(0, -1);

    return html;
}

function checkFormDataGiven(data) {
    var title = false;
    var date = false;
    var time = false;
    var project = false;
    var types = false;

    for (var i = 0; i < data.length; i++) {
        if (data[i].name == 'mapathonTitle' && data[i].value != "") {
            title = true;
        }
        else if (data[i].name == 'mapathonDate' && data[i].value != "") {
            date = true;
        }
        else if (data[i].name == 'mapathonTime' && data[i].value != "") {
            time = true;
        }
        else if (data[i].name == 'projectNumber' && data[i].value != "") {
            project = true;
        }
        else if (data[i].name == 'typesOfMapping') {
            types = true;
        }
    }
    
    return (title && date && time && project && types);
}

function createMapathonStatPageQueryParamsFromFormData(data) {
    //console.log(data);
    var html = "";
    var title = "";
    var date = "";
    var time = "";
    var project = "";

    for (var i = 0; i < data.length; i++) {
        if (data[i].name == 'mapathonTitle') {
            title += 'title=' + encodeURIComponent(data[i].value);
        }
        if (data[i].name == 'mapathonDate') {
            date += '&date=' + data[i].value;
        }
        if (data[i].name == 'mapathonTime') {
            time += '&time=' + data[i].value;
        }
        if (data[i].name == 'projectNumber') {
            project += '&project=' + data[i].value;
        }
    }
    html += title + date + time + project;
    html += '&types=';
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == 'typesOfMapping') {
            html += data[i].value + ',';
        }
    }

    html = html.slice(0, -1);

    return html;
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
            projectNumberAwesomplete = new Awesomplete(input, { // http://leaverou.github.io/awesomplete/
                list: awesompleteList,
                minChars: 1,
                filter: filterProject,
                replace: replaceProjectInputText
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

/**
 * Awesomplete filter
 * @param {string} text 
 * @param {string} input 
 */
function filterProject(text, input) {
    var parts = input.split(',');
    for (var i = 0; i < parts.length; i++) {
        if (text.indexOf(parts[i].trim()) >= 0) {
            return true;
        }
    }
    return false;
}

function replaceProjectInputText(selectedOptionText) {

    var parts = $("#projectNumber").val().split(',');
    var text = "";
    for (var i = 0; i < parts.length - 1; i++) {
        text += parts[i] + ",";
    }
    text += selectedOptionText.slice(1, selectedOptionText.indexOf(' ', 1));

    $("#projectNumber").val(text);
}
