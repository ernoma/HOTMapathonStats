
var projects = [];
var projectNumberAwesomplete = null;
var projectSelectedNumber = null;

$(document).ready(function () {
    getProjectSearchPage(1);
});

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