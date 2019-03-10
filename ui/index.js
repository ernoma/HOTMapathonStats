
var projects = [];
var projectNumberAwesomplete = null;
var projectSelectedNumber = null;

var submittedHOTOSMFormData = null;

var spinner = [];


/*
 * Called when the HTML page has been fully loaded to the web browser
 */
$(document).ready(function () {

    serverURL = "http://" + window.location.hostname + ":5000";

    getMapathons();

    getProjectSearchPage(1);

    $("#createStatisticsForm").submit(createStatistics);
});

//
// Functions for listing and showing existing mapathon statistics
//

/**
 * Gets the list of mapthon statitics from the server
 * 
 * @returns {array} The list of the mapathons
 */
function getMapathons() {

    createListSpinner();

    return $.getJSON(serverURL + "/mapathon/list", handleMapathonsData);
}

/**
 * Creates HTML for each mapathon list item and adds the items to a list in the UI
 * 
 * @param {array} data The list of the mapathons
 */
function handleMapathonsData(data) {
    console.log(data);

    removeListSpinner();

    data.forEach(item => {
        var html = '<div class="card"><div class="card-body"><h5 class="card-title">' + item.mapathon_info.mapathon_title + '</h5>' +
            '<p class="card-text">Mapathon held on ' +
            item.mapathon_info.mapathon_date + ' at ' +
            item.mapathon_info.mapathon_time_utc + ' (UTC) for the ';

            if (item.mapathon_info.project_numbers == undefined) {
                html += ' project ';
                html += '<a target="_blank" href="https://tasks.hotosm.org/project/' + item.mapathon_info.project_number + '">' + item.mapathon_info.project_number + '</a>';
            }
            else {
                if (item.mapathon_info.project_numbers.length == 1) {
                    html += ' project ';
                }
                else {
                    html += ' projects ';
                    for (var i = 0; i < item.mapathon_info.project_numbers.length - 1; i++) {
                        var project_number = item.mapathon_info.project_numbers[i];
                        html += '<a target="_blank" href="https://tasks.hotosm.org/project/' + project_number + '">' + project_number + '</a>' + ', ';
                    }
                    html = html.slice(0, -2) + ' and ';
                    var project_number = item.mapathon_info.project_numbers[item.mapathon_info.project_numbers.length - 1];
                    html += '<a target="_blank" href="https://tasks.hotosm.org/project/' + project_number + '">' + project_number + '</a>';
                }
            }

            html += '</p>' +
            // item.mapathon_users.length + ' <i class="fa fa-user" aria-hidden="true"></i></p>' +
            '<p><a target="_blank" href="stats?' +
            createMapathonStatPageQueryParamsForItem(item);
        html += '&id=' + item._id.$oid;
        html +=
            '" id="' + item._id.$oid + '" class="btn btn-primary">Show statistics page</a></p></div></div>';
        $("#mapathonList").append(html);

        //$("#" + item._id.$oid).on('click', showMapathon);
    });
}

// function showMapathon(event) {
//     // TODO use event.target.id to show mapathon statistics page
//     //console.log(event);
// }

//
// Functions for creating mapathon statistics
//

/**
 * Handles the form submit event caused by the user.
 * Starts the statistics creation on the server.
 * 
 * @param {Event} event The form submit event
 */
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

/**
 * Creates HTML link with description for the statistics page that is being created. 
 * 
 * @param {string} stat_task_uuid UUID for the mapathon statistics received from the server. 
 * @returns {string} HTML link with description
 */
function getStatsURLCopyInfo(stat_task_uuid) {
    return "Provided that the statistics are created succesfully, you can find the result page later on the created mapathon statistics list and at the address<br>" +
        "<input type='text' size='40' id='spanStatsURL' value='" +
        window.location.href + "stats?" + 
        createMapathonStatPageQueryParamsFromFormData(submittedHOTOSMFormData) + 
        "&uid=" + stat_task_uuid +
        "'>&nbsp<button class='btn btn-primary' onclick='text=document.getElementById(\"spanStatsURL\").select();document.execCommand(\"copy\");'>Copy</button>" +
        "<br>You can safely close this page now."
}

/**
 * Gets the current state of the mapathon statistics creation from the server and informs user via UI of the statistics creation progress.
 * 
 * @param {string} stat_task_uuid 
 */
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

/**
 * Creates URL query parameter string using the item that contains information of the mapathon recevied from the server
 * 
 * @param {object} item mapathon item that contains the data that was recevied from the server
 * @returns {string} URL query parameter string
 */
function createMapathonStatPageQueryParamsForItem(item) {
    var html = "";
    html += 'title=' + encodeURIComponent(item.mapathon_info.mapathon_title) +
    '&date=' + item.mapathon_info.mapathon_date +
    '&time=' + item.mapathon_info.mapathon_time_utc +
    '&projects=';

    if (item.mapathon_info.project_numbers == undefined) {
        html += item.mapathon_info.project_number;
    }
    else {
        item.mapathon_info.project_numbers.forEach(project_number => {
            html += project_number + ',';
        });
        html = html.slice(0, -1);
    }
    html += '&types=';
    item.mapathon_info.types_of_mapping.forEach(type => {
        html += type + ','
    });
    html = html.slice(0, -1);

    return html;
}

/**
 * Does some basic sanity checks for the form data before trying to create mapathon statistics
 * 
 * @param {array} data The form data
 * @returns {boolean} True if sanity check passes, otherwise false
 */
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
        else if (data[i].name == 'projectNumbers' && data[i].value != "") {
            project = true;
        }
        else if (data[i].name == 'typesOfMapping') {
            types = true;
        }
    }
    
    return (title && date && time && project && types);
}

/**
 * Creates URL query parameter string using the item that contains information of the mapathon inputted by user in the UI form
 * 
 * @param {object} data contains the mapathon data that user inputted to the form
 * @returns {string} URL query parameter string
 */
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
        if (data[i].name == 'projectNumbers') {
            project += '&projects=' + data[i].value.replace(/ /g,'');
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

/**
 * Hides possibly shown info alerts in the UI
 */
function hideAlerts() {
    $("#serverSuccessAlert").hide();
    $("#serverErrorAlert").hide();
}

/**
 * Gets list of the HOT Tasking Manager projects on the specified page from the tasks.hotosm.org API
 * 
 * @param {integer} page The page URL query parameter used in the mapathon list REST call
 */
function getProjectSearchPage(page) {

    var params = {
        page: page
    };

    $.getJSON("https://tasks.hotosm.org/api/v1/project/search", params, function (data) {
        projects = projects.concat(data.results);
        //console.log(data);
        //console.log(projects);

        var input = document.getElementById("projectNumbers");

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

        Awesomplete.$('#projectNumbers').addEventListener("awesomplete-selectcomplete", function() {
            projectSelectedNumber = $('#projectNumbers').val();
            projectNumberAwesomplete.close();
        });
        Awesomplete.$('#projectNumbers').addEventListener("awesomplete-open", function () {
            if (projectSelectedNumber == $('#projectNumbers').val()) {
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
 * Awesomplete filter that return true if the project number form input contains the text
 * 
 * @param {string} text item text provided by Awesomplete from the list of items it has been provided
 * @param {string} input form input text for the Tasking manager project numbers
 * @returns {boolean} True if the input contains the text, otherwise false
 * 
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

/**
 * Updates the project number form input with the autocomplete selection
 * 
 * @param {string} selectedOptionText text of the Awesomplete item that the user chose from the autocompletion list
 */
function replaceProjectInputText(selectedOptionText) {

    var parts = $("#projectNumbers").val().split(',');
    var text = "";
    for (var i = 0; i < parts.length - 1; i++) {
        text += parts[i] + ",";
    }
    text += selectedOptionText.slice(1, selectedOptionText.indexOf(' ', 1));

    $("#projectNumbers").val(text);
}


function createListSpinner() {
    var opts = {
        lines: 20, // The number of lines to draw
        length: 13, // The length of each line
        width: 8, // The line thickness
        radius: 9, // The radius of the inner circle
        scale: 1, // Scales overall size of the spinner
        corners: 1, // Corner roundness (0..1)
        color: '#7674e5', // CSS color or array of colors
        fadeColor: 'transparent', // CSS color or array of colors
        speed: 1, // Rounds per second
        rotate: 0, // The rotation offset
        animation: 'spinner-line-fade-more', // The CSS animation name for the lines
        direction: 1, // 1: clockwise, -1: counterclockwise
        zIndex: 2e9, // The z-index (defaults to 2000000000)
        className: 'spinner', // The CSS class to assign to the spinner
        top: '100px', // Top position relative to parent
        left: '50%', // Left position relative to parent
        shadow: '0 0 1px transparent', // Box-shadow for the lines
        position: 'absolute' // Element positioning
      };

      var target = document.getElementById('listSpinner');
      spinner = new Spinner(opts).spin(target);
}

function removeListSpinner() {
    spinner.stop();
}