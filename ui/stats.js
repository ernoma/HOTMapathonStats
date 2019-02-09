
var map = undefined;

var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18
});

var hotLayer = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Tiles courtesy of <a href="http://hot.openstreetmap.org/">Humanitarian OpenStreetMap Team</a>',
    maxZoom: 18
});

var bingLayer = new L.BingLayer('AuJOP1AQnHgJ50Co_d_mnn8ZSyoCN71Mcv6Ve3S_xOQqyyrBFaWnNIcy-6GX-nX_', {type: 'AerialWithLabels'});

var baseMaps = {
    "OpenStreetMap": osmLayer,
    "Humanitarian": hotLayer,
    "Bing aerial": bingLayer
}

var roadStats = {
    whenApplyCountRemaining: undefined,
    lengthSum: 0,
    count: 0,
    modifiedCount: 0
}

var landuseStats = {
	whenApplyCountRemaining: undefined,
    lengthSum: 0,
    count: 0,
    modifiedCount: 0
}

const urlParams = new URLSearchParams(window.location.search);

var projectHOTOSMData = null;

const serverURL = "http://" + window.location.hostname + ":5000";

var timeDimension = null;
var timePlayer = null;

$(document).ready(function () {
	
    map = L.map('map_canvas', {
		layers: [osmLayer]
	});
    L.control.layers(baseMaps).addTo(map);
    L.control.scale().addTo(map);

	initTimeDimensions();

	$.getJSON("https://tasks.hotosm.org/api/v1/project/" + urlParams.get("project"), function (projectData) {

		projectHOTOSMData = projectData;

		showMapathonBasicData();

		//console.log(data);

		var areaGEOJSON = L.geoJSON(projectData.tasks, {
			style: function (feature) {
				return {color: '#999999', weight: 1, fill: false }
			}
		});
		areaGEOJSON.addTo(map);
		map.fitBounds(areaGEOJSON.getBounds());

		//showPriorityAreas();

		showMissingMapsData();

		showStatistics();
    });
});

function initTimeDimensions() {

	var minTime = "2018-01-01T00:00:00";
	var maxTime = "2020-01-01T00:00:00";

	timeDimension = new L.TimeDimension({
		timeInterval: minTime + "/" + maxTime,
		period: "PT5M"
	});

	map.timeDimension = timeDimension;

	timePlayer = new L.TimeDimension.Player({
		transitionTime: 200, 
		loop: false,
		startOver:true
	}, timeDimension);

	var timeDimensionControlOptions = {
		player:        timePlayer,
		timeDimension: timeDimension,
		position:      'bottomleft',
		autoPlay:      false,
		minSpeed:      1,
		speedStep:     0.5,
		maxSpeed:      15,
		timeSliderDragUpdate: true
	};

	var timeDimensionControl = new L.Control.TimeDimension(timeDimensionControlOptions);
	map.addControl(timeDimensionControl);
}

function showStatistics() {

	//console.log(urlParams.get("types"));

	var types = urlParams.get("types").split(',');

	types.forEach((type) => {
		if (type == 'building') {
			createBuildingSectionElements();
			createBuildingStatistics();
		}
		else if (type == 'landuse_residential') {
			createResidentialAreaSectionElements();
			createResidentialAreaStatistics();
		}
		else if(type == 'landuse_any_other') {
			createLanduseAnyOtherSectionElements();
			createLanduseAnyOtherSectionStatistics();
		}
		else { // type == 'highway'
			createRoadSectionElements();
			createRoadStatistics();
		}
	});

	// var data_dirs = ["tanzania/"];
	// createRoadStatistics(data_dirs);
	// //createResidentialAreaStatistics(data_dirs);
	// createBuildingStatistics(data_dirs);


}

function createBuildingSectionElements() {
	var buildingsSectionHTML =
		'<h3>Buildings</h3>' +
		'<div class="row top-buffer bottom-buffer">' +
	  	'<div class="col-sm-3">Buildings, total count</div>' +
		'<div class="col-sm-9" id="building_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>';

	$("#buildingsSection").html(buildingsSectionHTML);
}

function createResidentialAreaSectionElements() {
	var residentialAreasSectionHTML =
		'<h3>Residential Areas</h3>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Residential areas, total count</div>' +
		'<div class="col-sm-9"id="res_area_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Residential areas, total area</div>' +
		'<div class="col-sm-9" id="res_area_total_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row bottom-buffer">' +
		'<div class="col-sm-3">Residential areas, average area</div>' +
		'<div class="col-sm-9" id="res_area_avg_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>';
		
	$("#residentialAreasSection").html(residentialAreasSectionHTML);
}

function createLanduseAnyOtherSectionElements() {
	var landuseAnyOtherSectionHTML =
		'<h3>Other landuse</h3>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Farmlands, total count</div>' +
		'<div class="col-sm-9"id="landuse_farmland_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Farmlands, total area</div>' +
		'<div class="col-sm-9" id="landuse_farmland_total_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Farmlands, average area</div>' +
		'<div class="col-sm-9" id="landuse_farmland_avg_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Orchards, total count</div>' +
		'<div class="col-sm-9"id="landuse_orchard_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Orchards, total area</div>' +
		'<div class="col-sm-9" id="landuse_orchard_total_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Orchards, average area</div>' +
		'<div class="col-sm-9" id="landuse_orchard_avg_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Other, total count</div>' +
		'<div class="col-sm-9"id="landuse_any_other_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Other, total area</div>' +
		'<div class="col-sm-9" id="landuse_any_other_total_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Other, average area</div>' +
		'<div class="col-sm-9" id="landuse_any_other_avg_area_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>';
		
	$("#landuseAnyOtherSection").html(landuseAnyOtherSectionHTML);
}

function createRoadSectionElements() {
	
	var highwaysSectionHTML =
		'<h3>Roads and Paths</h3>' +
		'<div class="row">' +
		'<div class="col-sm-3">Primary roads created, length</div>' +
		'<div class="col-sm-3" id="primary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Secondary roads created, length</div>' +
		'<div class="col-sm-3" id="secondary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Tertiary roads created, length</div>' +
		'<div class="col-sm-3" id="tertiary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Unclassified roads created, length</div>' +
		'<div class="col-sm-3" id="un_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Residential roads created, length</div>' +
		'<div class="col-sm-3" id="res_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Service roads created, length</div>' +
		'<div class="col-sm-3" id="service_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Tracks created, length</div>' +
		'<div class="col-sm-3" id="tracks_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Paths created, length</div>' +
		'<div class="col-sm-3" id="paths_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Footways created, length</div>' +
		'<div class="col-sm-3" id="footway_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">(*) Other roads created, length</div>' +
		'<div class="col-sm-3" id="highway_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Roads created, total length</div>' +
		'<div class="col-sm-9" id="roads_total_length_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row top-buffer">' +
		'<div class="col-sm-3">Primary roads, count</div>' +
		'<div class="col-sm-3" id="primary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Secondary roads, count</div>' +
		'<div class="col-sm-3" id="secondary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Tertiary roads, count</div>' +
		'<div class="col-sm-3" id="tertiary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Unclassified roads, count</div>' +
		'<div class="col-sm-3" id="un_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Residential roads, count</div>' +
		'<div class="col-sm-3" id="res_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Service roads, count</div>' +
		'<div class="col-sm-3" id="service_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Tracks, count</div>' +
		'<div class="col-sm-3" id="tracks_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">Paths, count</div>' +
		'<div class="col-sm-3" id="paths_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row">' +
		'<div class="col-sm-3">Footways created, count</div>' +
		'<div class="col-sm-3" id="footway_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'<div class="col-sm-3">(*) Other roads created, count</div>' +
		'<div class="col-sm-3" id="highway_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'<div class="row top-buffer bottom-buffer">' +
		'<div class="col-sm-3">Roads and paths, total count</div>' +
		'<div class="col-sm-3" id="roads_total_count_div"><i class="fa fa-spinner fa-pulse"></i></div>' +
		'</div>' +
		'</div>	' +
		'<hr>' +
		'<p id="data_note">(*) Other roads means ways that were tagged highway=road, highway=motorway, highway=trunk or highway=living_street. See the OSM <a href="http://wiki.openstreetmap.org/wiki/Key:highway">highway tagging wiki</a> page (and in Africa <a href="https://wiki.openstreetmap.org/wiki/Highway_Tag_Africa">Highway Tag Africa wiki page</a>) for more information on the types.' +
		'</p>';

	  $("#highwaysSection").html(highwaysSectionHTML);
}

function showPriorityAreas() {
    
    var priority_areas = {
	
    };

    L.geoJson(priority_areas, {
	style: function (feature) {
            return {color: "#F00", fill: false, weight: 2, opacity: 0.8};
	}
    }).addTo(map);
}

function createRoadStatistics() {
    
    var parameters = [
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_primary"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_secondary"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_tertiary"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_unclassified"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_residential"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_service"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_track"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_path",
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_footway"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "highways_road"
		}
	];

	var highwayJSONCalls = {
		primary: [],
		secondary: [],
		tertiary: [],
		unclassified: [],
		residential: [],
		service: [],
		track: [],
		path: [],
		footway: [],
		road: []
	};	

    roadStats.whenApplyCountRemaining = 10;
    
	highwayJSONCalls.primary.push(readJSONData(serverURL + '/mapathon/data', parameters[0]));
	highwayJSONCalls.secondary.push(readJSONData(serverURL + '/mapathon/data', parameters[1]));
	highwayJSONCalls.tertiary.push(readJSONData(serverURL + '/mapathon/data', parameters[2]));
	highwayJSONCalls.unclassified.push(readJSONData(serverURL + '/mapathon/data', parameters[3]));
	highwayJSONCalls.residential.push(readJSONData(serverURL + '/mapathon/data', parameters[4]));
	highwayJSONCalls.service.push(readJSONData(serverURL + '/mapathon/data', parameters[5]));
	highwayJSONCalls.track.push(readJSONData(serverURL + '/mapathon/data', parameters[6]));
	highwayJSONCalls.path.push(readJSONData(serverURL + '/mapathon/data', parameters[7]));
	highwayJSONCalls.footway.push(readJSONData(serverURL + '/mapathon/data', parameters[8]));
	highwayJSONCalls.road.push(readJSONData(serverURL + '/mapathon/data', parameters[9]));

    $.when.apply($, highwayJSONCalls.primary).done(handleRoadStatisicsData("#primary_road_length_div", "#primary_road_count_div", '#F00', 4, null));
    $.when.apply($, highwayJSONCalls.secondary).done(handleRoadStatisicsData("#secondary_road_length_div", "#secondary_road_count_div", '#FFA500', 3, null));
    $.when.apply($, highwayJSONCalls.tertiary).done(handleRoadStatisicsData("#tertiary_road_length_div", "#tertiary_road_count_div", '#FFFF00', 3, null));
    $.when.apply($, highwayJSONCalls.unclassified).done(handleRoadStatisicsData("#un_road_length_div", "#un_road_count_div", '#000', 2, null));
    $.when.apply($, highwayJSONCalls.residential).done(handleRoadStatisicsData("#res_road_length_div", "#res_road_count_div", '#FFF', 2, null));
    $.when.apply($, highwayJSONCalls.service).done(handleRoadStatisicsData("#service_road_length_div", "#service_road_count_div", '#FFF', 2, null));
    $.when.apply($, highwayJSONCalls.track).done(handleRoadStatisicsData("#tracks_length_div", "#tracks_count_div", '#D27259', 2, "5 2"));
    $.when.apply($, highwayJSONCalls.path).done(handleRoadStatisicsData("#paths_length_div", "#paths_count_div", '#D29259', 2, "5 5"));
    $.when.apply($, highwayJSONCalls.footway).done(handleRoadStatisicsData("#footway_length_div", "#footway_count_div", '#D29200', 2, "3 5"));
    $.when.apply($, highwayJSONCalls.road).done(handleRoadStatisicsData("#highway_road_length_div", "#highway_road_count_div", '#FFA', 2, null));
}

function createResidentialAreaStatistics(data_dirs) {
    var ajaxCalls = [];
	
	parameters = {
		id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
		type: "landuse_residential"
	}

	ajaxCalls.push(readJSONData(serverURL + '/mapathon/data', parameters));

    $.when.apply($, ajaxCalls).done(function() {
		//console.log(arguments);
		var elements = null;
		if (arguments.length > 1 && arguments[1].constructor === Array) {
			elements = arguments[0][0];
			combineElements(elements, Array.from(arguments).slice(1));
		}
		else {
			elements = arguments[0];
		}
		
		calculateResidentialAreaStatistics(elements);
    });
}

function createLanduseAnyOtherSectionStatistics(data_dirs) {
	var parameters = [
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "landuse_farmland"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "landuse_orchard"
		},
		{
			id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
			type: "landuse_any_other"
		}
	];

	var landuseJSONCalls = {
		farmland: [],
		orchard: [],
		any_other: []
	};	

    landuseStats.whenApplyCountRemaining = 3;
    
	landuseJSONCalls.farmland.push(readJSONData(serverURL + '/mapathon/data', parameters[0]));
	landuseJSONCalls.orchard.push(readJSONData(serverURL + '/mapathon/data', parameters[1]));
	landuseJSONCalls.any_other.push(readJSONData(serverURL + '/mapathon/data', parameters[2]));

    $.when.apply($, landuseJSONCalls.farmland).done(handleLandusetatisicsData("Farmland", "landuse_farmland", '#9b6a25', 2));
    $.when.apply($, landuseJSONCalls.orchard).done(handleLandusetatisicsData("Orchard", "landuse_orchard", '#1a420b', 2));
    $.when.apply($, landuseJSONCalls.any_other).done(handleLandusetatisicsData("Other landuse", "landuse_any_other", '#9cb3bf', 2));
}

function createBuildingStatistics() {
    var ajaxCalls = [];

	parameters = {
		id: urlParams.get("id") != null ? urlParams.get("id") : urlParams.get("uid"),
		type: "building"
	}

	ajaxCalls.push(readJSONData(serverURL + '/mapathon/data', parameters));

    $.when.apply($, ajaxCalls).done(function() {
		//console.log(arguments);
		var elements = null;
		if (arguments.length > 1 && arguments[1].constructor === Array) {
			elements = arguments[0][0];
			combineElements(elements, Array.from(arguments).slice(1));
		}
		else {
			elements = arguments[0];
		}
		//console.log(elements);
		calculateBuildingStatistics(elements);
    });
}

function readJSONData(dataURL, parameters) {
    return $.getJSON(dataURL, parameters);
}   

function calculateBuildingStatistics(elements) {

    var buildingsCount = 0;
    var modifiedCount = 0;
	
	var geoJSONFeatures = [];

	for (var i = 0; i < elements.length; i++) {
        var building = elements[i];

		if (building.type != undefined && building.type == 'Feature') { // GeoJSON
			if (building.properties.version != 1) {
				modifiedCount++;
			}
			else {
				geoJSONFeatures.push(building);
				buildingsCount++;
			}
		}
		else {
			if (building.version != 1) {
				modifiedCount++;
			}
			else {
				var latLngs = [];
				buildingsCount++;
				for (var j = 0; j < building.nodes.length; j++) {
					latLngs.push(L.latLng(building.nodes[j].lat, building.nodes[j].lon));
				}
				if (latLngs.length > 2) {
					var polygon = L.polygon(latLngs, {color: '#FF0000', weight: 2 });
					var linkText = 'Building, id: ' + building.id;
					//var linkText = '<a href="http://www.openstreetmap.org/way/' + building.id + '" target="_blank">View on openstreetmap.org</a>';
					polygon.bindPopup(linkText);
					polygon.addTo(map);
				}
			}
		}
	}
	
	if (geoJSONFeatures.length >= 0) {
		//console.log(geoJSONFeatures);

		var geojsonLayer = L.geoJSON(geoJSONFeatures, {
			style: {color: '#FF0000', weight: 2 },
			onEachFeature: function (feature, layer) {
				linkText = 'Building, id: ' + feature.properties.id;
				layer.bindPopup(linkText);
			}
		});

		var timeDimensionLayer = L.timeDimension.layer.geoJson(geojsonLayer, {
			addlastPoint: false,
			updateTimeDimension: true
		});

		timeDimensionLayer.addTo(map);
		var times = timeDimension.getAvailableTimes();
		timeDimension.setCurrentTime(times[times.length - 1]);
	}

    var modifiedPercentage = elements.length == 0 ? 0 : modifiedCount / elements.length * 100;
    var text = "" + buildingsCount + ", +" + modifiedCount + " modified" + " (" + modifiedPercentage.toFixed(1) + "%)";

    $("#building_count_div").text(text);
}

function calculateResidentialAreaStatistics(elements) {
    var residentialAreaCount = 0;
    var residentialAreaNonEmptyCount = 0;
    var totalArea = 0;
    var modifiedCount = 0;

	var geoJSONFeatures = [];

    for (var i = 0; i < elements.length; i++) {
        var residentialArea = elements[i];

		if (residentialArea.type != undefined && residentialArea.type == 'Feature') { // GeoJSON
			if (residentialArea.properties.version != 1) {
				modifiedCount++;
			}
			else {
				geoJSONFeatures.push(residentialArea);
				residentialAreaCount++;
				residentialAreaNonEmptyCount++;
				var area = turf.area(residentialArea.geometry);
				totalArea += area;
			}
		}
		else {
			if (residentialArea.version != 1) {
				modifiedCount++;
			}
			else {	    
				var area = 0;
				var latLngs = [];
				residentialAreaCount++;
				for (var j = 0; j < residentialArea.nodes.length; j++) {
					latLngs.push(L.latLng(residentialArea.nodes[j].lat, residentialArea.nodes[j].lon));
				}
				if (latLngs.length > 2) {
					residentialAreaNonEmptyCount++;
					var polygon = L.polygon(latLngs, {color: '#FFFF00', weight: 2 });
					var linkText = 'Residental area, id: ' + residentialArea.id;
					//var linkText = '<a href="http://www.openstreetmap.org/way/' + residentialArea.id + '" target="_blank">View on openstreetmap.org</a>';
					polygon.bindPopup(linkText);
					polygon.addTo(map);
					area = L.GeometryUtil.geodesicArea(latLngs); // in squaremeters
					totalArea += area;
				}
			}
		}
    }

	if (geoJSONFeatures.length >= 0) {
		//console.log(geoJSONFeatures);
		var geojsonLayer = L.geoJSON(geoJSONFeatures, {
			style: {color: '#FFFF00', weight: 2 },
			onEachFeature: function (feature, layer) {
				linkText = 'Residental area, id: ' + feature.properties.id;
				layer.bindPopup(linkText);
			}
		});
		
		var timeDimensionLayer = L.timeDimension.layer.geoJson(geojsonLayer, {
			addlastPoint: false,
			updateTimeDimension: true
		});

		timeDimensionLayer.addTo(map);
		var times = timeDimension.getAvailableTimes();
		timeDimension.setCurrentTime(times[times.length - 1]);
	}

    var modifiedPercentage = elements.length == 0 ? 0 : modifiedCount / elements.length * 100;
    var text = "" + residentialAreaCount + ", +" + modifiedCount + " modified" + " (" + modifiedPercentage.toFixed(1) + "%)";
	
	$("#res_area_count_div").text(text);
    $("#res_area_total_area_div").html(Math.round(totalArea) + " m<sup>2</sup>");
    $("#res_area_avg_area_div").html(Math.round(totalArea / residentialAreaNonEmptyCount) + " m<sup>2</sup>");
}

function calculateWaterwayStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray) {
    return calculateWayStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray);
}

function calculateRoadStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray) {
    return calculateWayStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray);
}

function calculateWayStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray) {
    var waysCount = 0;
    var totalWayLength = 0;
    var modifiedCount = 0;
	
	var geoJSONFeatures = [];

    for (var i = 0; i < elements.length; i++) {

		if (elements[i].type != undefined && elements[i].type == 'Feature') { // GeoJSON
			if (elements[i].properties.version != 1) {
				modifiedCount++;
			}
			else {
				geoJSONFeatures.push(elements[i]);
				waysCount++;
				var wayDistance = turf.length(elements[i].geometry) * 1000;
				totalWayLength += wayDistance;
			}
		}
		else {
			if (elements[i].version != 1) {
				modifiedCount++;
			}
			else {
				var wayDistance = 0;
				var latLngs = [];
				waysCount++;
				for (var j = 0; j < elements[i].nodes.length; j++) {
					latLngs.push(L.latLng(elements[i].nodes[j].lat, elements[i].nodes[j].lon));
				}
				var polyLine = L.polyline(latLngs, {weight: weight, color: mapLineColor, dashArray: dashArray });
				var wayTextSuffix = "";
				var linkText = "";
				if (elements[i].tags.highway != undefined) {
					if (elements[i].tags.highway != "track" && elements[i].tags.highway != "path"
						&& elements[i].tags.highway != "road" && elements[i].tags.highway != "footway") {
						wayTextSuffix = " road";
					}
					linkText = elements[i].tags.highway + wayTextSuffix + ', id: ' + elements[i].id;
					//var linkText = '<a href="http://www.openstreetmap.org/way/' + elements[i].id + '" target="_blank">View on openstreetmap.org</a>';
				}
				else if (elements[i].tags.waterway != undefined) {
					linkText = elements[i].tags.waterway + wayTextSuffix + ', id: ' + elements[i].id;
					//console.log(linkText);
				}
				polyLine.bindPopup(linkText);
				polyLine.addTo(map);
			
				for (var j = 0; j < latLngs.length - 1; j++) {
					var lat1 = latLngs[j].lat;
					var lon1 = latLngs[j].lng;
					var lat2 = latLngs[j+1].lat;
					var lon2 = latLngs[j+1].lng;
					wayDistance += distance(lat1,lon1,lat2,lon2) * 1000;
				}

				totalWayLength += wayDistance;
			}
		}
    }
	
	if (geoJSONFeatures.length >= 0) {
		//console.log(geoJSONFeatures);
		var geojsonLayer = L.geoJSON(geoJSONFeatures, {
			style: {color: mapLineColor, weight: weight, dashArray: dashArray },
			onEachFeature: function (feature, layer) {
				var wayTextSuffix = "";
				var linkText = "";
				if (feature.properties.tags.highway != undefined) {
					if (feature.properties.tags.highway != "track" && feature.properties.tags.highway != "path"
						&& feature.properties.tags.highway != "road" && feature.properties.tags.highway != "footway") {
						wayTextSuffix = " road";
					}
					linkText = feature.properties.tags.highway + wayTextSuffix + ', id: ' + feature.properties.id;
					//var linkText = '<a href="http://www.openstreetmap.org/way/' + elements[i].id + '" target="_blank">View on openstreetmap.org</a>';
				}
				else if (feature.properties.tags.waterway != undefined) {
					linkText = feature.properties.tags.waterway + wayTextSuffix + ', id: ' + feature.properties.id;
					//console.log(linkText);
				}
				layer.bindPopup(linkText);
			}
		});
		
		var timeDimensionLayer = L.timeDimension.layer.wayLayer(geojsonLayer, {
			addlastPoint: false,
			updateTimeDimension: true
		});

		timeDimensionLayer.addTo(map);
		var times = timeDimension.getAvailableTimes();
		timeDimension.setCurrentTime(times[times.length - 1]);
	}

    var length = totalWayLength / 1000;
    var text = "" + length.toFixed(1) + " km";
    $(lengthHtmlElementID).text(text);
    //console.log(totalWayLength);
    
    var modifiedPercentage = elements.length == 0 ? 0 : modifiedCount / elements.length * 100;
    text = "" + waysCount + ", +" + modifiedCount + " modified (" + modifiedPercentage.toFixed(1) + "%)";
    $(countHtmlElementID).text(text);

    return { "length": totalWayLength, "createdCount": waysCount, "modifiedCount": modifiedCount };
}

function distance(lat1, lon1, lat2, lon2) {
  var p = 0.017453292519943295;    // Math.PI / 180
  var c = Math.cos;
  var a = 0.5 - c((lat2 - lat1) * p)/2 + 
          c(lat1 * p) * c(lat2 * p) * 
          (1 - c((lon2 - lon1) * p))/2;

  return 12742 * Math.asin(Math.sqrt(a)); // 2 * R; R = 6371 km
}

function handleRoadStatisicsData(lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray) {
    return function(data, textStatus, jqXHR) {
		//console.log(arguments);
		var elements = null;
		if (arguments.length > 1 && arguments[1].constructor === Array) {
			elements = arguments[0][0];
			combineElements(elements, Array.from(arguments).slice(1));
		}
		else {
			elements = arguments[0];
		}
		var result = calculateRoadStatistics(elements, lengthHtmlElementID, countHtmlElementID, mapLineColor, weight, dashArray);
		roadStats.lengthSum += result.length;
		roadStats.count += result.createdCount;
		roadStats.modifiedCount += result.modifiedCount;
		
		roadStats.whenApplyCountRemaining--;
		if (roadStats.whenApplyCountRemaining == 0) {
			$("#roads_total_length_div").text("" + Math.round(roadStats.lengthSum / 1000) + " km");
			var modifiedPercentage = roadStats.modifiedCount / (roadStats.modifiedCount + roadStats.count) * 100;
			$("#roads_total_count_div").text("" + roadStats.count + ", +" + roadStats.modifiedCount + " modified (" + modifiedPercentage.toFixed(1) + "%)");
		}
    };
}

function handleLandusetatisicsData(userFriendlyName, typeHtmlElementPrefix, color, weight) {
	return function(data, textStatus, jqXHR) {
		var elements = null;
		if (arguments.length > 1 && arguments[1].constructor === Array) {
			elements = arguments[0][0];
			combineElements(elements, Array.from(arguments).slice(1));
		}
		else {
			elements = arguments[0];
		}

		calculateLanduseStatistics(elements, userFriendlyName, typeHtmlElementPrefix, color, weight);
	};
}

function calculateLanduseStatistics(elements, userFriendlyName, typeHtmlElementPrefix, color, weight) {
	var landuseAreaCount = 0;
    var landuseAreaNonEmptyCount = 0;
    var totalArea = 0;
    var modifiedCount = 0;

	var geoJSONFeatures = [];

	//console.log("calculateLanduseStatistics", userFriendlyName, typeHtmlElementPrefix, color, weight);

    for (var i = 0; i < elements.length; i++) {
        var landuseArea = elements[i];

		if (landuseArea.type != undefined && landuseArea.type == 'Feature') { // GeoJSON
			if (landuseArea.properties.version != 1) {
				modifiedCount++;
			}
			else {
				geoJSONFeatures.push(landuseArea);
				landuseAreaCount++;
				landuseAreaNonEmptyCount++;
				var area = turf.area(landuseArea.geometry);
				totalArea += area;
			}
		}
		else {
			if(landuseArea.version != 1) {
				modifiedCount++;
			}
			else {	    
				var area = 0;
				var latLngs = [];
				landuseAreaCount++;
				for (var j = 0; j < landuseArea.nodes.length; j++) {
					latLngs.push(L.latLng(landuseArea.nodes[j].lat, landuseArea.nodes[j].lon));
				}
				if (latLngs.length > 2) {
					landuseAreaNonEmptyCount++;
					var polygon = L.polygon(latLngs, {color: color, weight: weight });
					var linkText = userFriendlyName + ', id: ' + landuseArea.id;
					//var linkText = '<a href="http://www.openstreetmap.org/way/' + residentialArea.id + '" target="_blank">View on openstreetmap.org</a>';
					polygon.bindPopup(linkText);
					polygon.addTo(map);
					area = L.GeometryUtil.geodesicArea(latLngs); // in squaremeters
					totalArea += area;
				}
			}
		}
    }

	if (geoJSONFeatures.length >= 0) {
		//console.log(geoJSONFeatures);
		var geojsonLayer = L.geoJSON(geoJSONFeatures, {
			style: {color: color, weight: weight },
			onEachFeature: function (feature, layer) {
				linkText = userFriendlyName + ', id: ' + feature.properties.id;
				layer.bindPopup(linkText);
			}
		});
		
		var timeDimensionLayer = L.timeDimension.layer.geoJson(geojsonLayer, {
			addlastPoint: false,
			updateTimeDimension: true
		});

		timeDimensionLayer.addTo(map);
		var times = timeDimension.getAvailableTimes();
		timeDimension.setCurrentTime(times[times.length - 1]);
	}

    var modifiedPercentage = elements.length == 0 ? 0 : modifiedCount / elements.length * 100;
    var text = "" + landuseAreaCount + ", +" + modifiedCount + " modified" + " (" + modifiedPercentage.toFixed(1) + "%)";
	
	$("#" + typeHtmlElementPrefix + "_count_div").text(text);
    $("#" + typeHtmlElementPrefix + "_total_area_div").html(Math.round(totalArea) + " m<sup>2</sup>");
    $("#" + typeHtmlElementPrefix + "_avg_area_div").html(Math.round(totalArea / landuseAreaNonEmptyCount) + " m<sup>2</sup>");
}

function combineElements(elements, elementArrays) {
    for (var d = 0; d < elementArrays.length; d++) {
		var elems = elementArrays[d][0];
		for (var i = 0; i < elems.length; i++) {
			if(!isInElements(elems[i], elements)) {
				elements.push(elems[i]);
			}
		}
    }
}

function isInElements(element, elements) {
    
    for (var i = 0; i < elements.length; i++) {
		if (elements[i].id == element.id) {
			return true;
		}
    }

    return false;
}

function showMapathonBasicData() {
	$("head title").text(urlParams.get("title"));
	// console.log(window.location.search);
	// console.log(urlParams.get("title"));
	$("#mapathonTitle").text(urlParams.get("title"));

	time_zone_info = urlParams.get("tz") != undefined ? '(' + urlParams.get("tz") + ')' : '(UTC)';

	$("#mapathonIntro").html(
		'<p>Data created on ' + moment(urlParams.get("date"), "YYYY-MM-DD").format("Do [of] MMM YYYY") +
		' from ' + urlParams.get("time") + ' ' + time_zone_info + '.</p>' +
		'<p>Some statistics for our contributions on the <a href="https://tasks.hotosm.org/project/' + urlParams.get("project") + '">#' + urlParams.get("project") + ' - ' + projectHOTOSMData.projectInfo.name + ' task</a>' +
		'.</p>'
	);
}

function showMissingMapsData() {
	var tags = projectHOTOSMData.changesetComment.split(" ");
	
	if (tags.length > 0) {
		var tagString = "";
		for (var i = 0; i < tags.length; i++) {
			tagString += tags[i].substr(1).toLowerCase() + ","

			//console.log(tags[i]);
			if (tags[i].startsWith('#hotosm-project-')) {
				getProjectUsers(tags[i].substr(1).toLowerCase());
			}
		}

		tagString = tagString.slice(0, -1);

		var html = 'the <a href="http://www.missingmaps.org/leaderboards/#/' +
		tagString +
		'">Missing Maps &uml;' +
		'project tags' +
		//projectHOTOSMData.changesetComment +
		'&uml; leaderboard</a> or ';

		html += 'the <ul>';
		for (var i = 0; i < tags.length; i++) {
			html += '<li><a href="http://www.missingmaps.org/leaderboards/#/' +
				tags[i].substr(1).toLowerCase() +
				'">Missing Maps ' +
				tags[i] +
					' leaderboard</a></li>';
		}

		html += '</ul> or ';

		$("#projectLeaderboardSpan").html(html);
	}
}

function getProjectUsers(tag) {
	// https://osm-stats-production-api.azurewebsites.net/hashtags/hotosm-project-3160/users?order_by=edits&order_direction=ASC&page=1
	$.getJSON("https://osm-stats-production-api.azurewebsites.net/hashtags/" + tag + "/users?order_by=edits&order_direction=ASC&page=1", function (users) {
		//console.log(users);
		if (users.length > 0) {
			var html = '';
			if (users.length < 500) {
				html += '<h2>Project Contributions by ' + users.length + ' Persons</h2>';

				html += '<div class="users">';
				
				for (var i = 0; i < users.length; i++) {
					html += '<div class="user">' +
						'<a href="http://tasks.hotosm.org/user/' + users[i].name + '">' + 
						users[i].name + 
						'</a>' +
						'</div>';
				}
				html += '</div>';
			}
			else {
				html += '<p>project contributions by over 500 persons</p>';
			}

			html += '<div class="userSectionAcknowledgements">The user list via Missing Maps (technical details: <a href="https://github.com/AmericanRedCross/osm-stats-api">github.com/AmericanRedCross/osm-stats-api</a>)<hr>';

			$("#usersSection").html(html);
		}
	});
}

if (!String.prototype.startsWith) {
	String.prototype.startsWith = function(searchString, position) {
		position = position || 0;
		return this.indexOf(searchString, position) === position;
	};
}


L.TimeDimension.Layer.WayLayer = L.TimeDimension.Layer.GeoJson.extend({

    // Do not modify features. Just return the feature if it intersects
    // the time interval
    _getFeatureBetweenDates: function(feature, minTime, maxTime) {
        var featureStringTimes = this._getFeatureTimes(feature);
        if (featureStringTimes.length == 0) {
            return feature;
        }
        var featureTimes = [];
        for (var i = 0, l = featureStringTimes.length; i < l; i++) {
            var time = featureStringTimes[i]
            if (typeof time == 'string' || time instanceof String) {
                time = Date.parse(time.trim());
            }
            featureTimes.push(time);
        }

        if (featureTimes[0] > maxTime || featureTimes[l - 1] < minTime) {
            return null;
        }
        return feature;
    },

});

L.timeDimension.layer.wayLayer = function(layer, options) {
    return new L.TimeDimension.Layer.WayLayer(layer, options);
};
