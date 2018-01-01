
var projects = [];
var projectNumberAwesomplete = null;
var projectSelectedNumber = null;

var serverURL = "http://localhost:5000";

$(document).ready(function () {
    getProjectSearchPage(1);

    $("#createStatisticsForm").submit(function(event) {
        event.preventDefault();
        hideAlerts();
        $("#serverSuccessAlert").text("Sending the data...");
        $("#serverSuccessAlert").show();
        var method = "/create/stats"
        $.ajax({
            type: 'POST',
            url: serverURL + method,
            data: $("#createStatisticsForm").serialize(),
            timeout: 10000,
            success: function (data) {
                console.log(data);
                if (data.status == 'OK') {
                    hideAlerts();
                    $("#serverSuccessAlert").text("Processing the data...");
                    $("#serverSuccessAlert").show();
                }
                else {
                    hideAlerts();
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
    });
});

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
