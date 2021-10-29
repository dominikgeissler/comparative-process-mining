var clicks = 0;
var col_data = "{{log_attributes.ColumnNamesValues}}";
col_data_parsed = JSON.parse(col_data.replace(/&quot;/g, '"'));
var Events = 0;
var Traces = 0;
var selectId = 0;
var idToGet = 0;
var leftGraphId = 0;
var rightGraphId = 0;
var Type_array = {
    ValueA: 'Frequency',
    ValueB: 'Performance'
};
var LDict = new Object();
var RDict = new Object();
var filename = new Object();
$(document).ready(function () {

    $('#SwitchToCompare').click(function () {
        $('#CompareModel-tab').trigger('click');
    });

    $(document).on("click", "button", function () {
        var buttonId = $(this).attr('id');
        selectId = buttonId.slice(-1);
        var RselectId = parseInt(selectId) + 1;
        leftGraphId = document.getElementById(selectId);
        rightGraphId = document.getElementById(RselectId);
        if (buttonId == ("B" + selectId)) {
            //alert("Inside B");
            leftGraphId = document.getElementById(selectId);
            leftGraphId.innerHTML = "";
            leftGraphId.setAttribute("style", "border : 1px solid #000000; height: 750px; width: 35%;float:left;");
            //alert(leftGraphId);
            rightGraphId = document.getElementById(RselectId);
            rightGraphId.innerHTML = "";
            rightGraphId.setAttribute("style", "border : 1px solid #000000; height: 750px; width: 35%;float:left;");
            GetFormValues(selectId, "L");
            GetFormValues((RselectId), "R");
            GetAjax(LDict, RDict, selectId, RselectId);
        }
        if (buttonId == ("P" + selectId)) {
            //alert("Inside P");
            printDiv(selectId, RselectId);
        }
        if (buttonId == ("LL" + selectId)) {
            //alert("Inside D");
            AjaxDownload(selectId)
        }
        if (buttonId == ("RL" + selectId)) {
            //alert("Inside D");
            AjaxDownload(RselectId)
        }
        if (buttonId == ("PrintLGraph" + selectId)) {
            //alert("Inside Lgraph");
            //printDiv(selectId, RselectId);
            var link = document.createElement('a');
            link.setAttribute('href', leftGraphId.firstElementChild.toDataURL("image/png").replace("image/png", "image/octet-stream"));
            link.setAttribute('download', 'LeftGraph.png');
            link.click();
            link.delete;
        }
        if (buttonId == ("PrintRGraph" + selectId)) {
            //alert("Inside Rgraph");
            //printDiv(selectId, RselectId);
            var link = document.createElement('a');
            link.setAttribute('href', rightGraphId.firstElementChild.toDataURL("image/png").replace("image/png", "image/octet-stream"));
            link.setAttribute('download', 'RightGraph.png');
            link.click();
            link.delete;
        }


    });


    $('#AddModel').click(function () {
        idToGet = clicks - 1;
        let dropdown = $('#LCN' + idToGet);
        let dropdownVal = $('#LCV' + idToGet);
        dropdown.empty();
        dropdownVal.empty();
        dropdown.append('<option selected="true" disabled>Choose Column</option>');
        dropdownVal.append('<option selected="true" disabled>Choose Column Value</option>');
        dropdown.prop('selectedIndex', 0);
        dropdownVal.prop('selectedIndex', 0);
        // Populate dropdown with list of columns
        $.each(col_data_parsed, function (key, entry) {
            dropdown.append($('<option></option>').attr('value', key).text(key));
        });

        $("select").on("change", function () {
            selectId = $(this).attr("id");
            var OptionSet = selectId.slice(0, -1);
            if (OptionSet == "LCN") {
                var selectedCol = $(("select#" + selectId + " option:selected")).text();
                var parsedColName = selectedCol.replaceAll('Choose Column', '');
                var colValues = col_data_parsed[parsedColName];
                updateSelectColValBox(colValues);
            }
            if (OptionSet == "RCN") {
                var selectedCol = $(("select#" + selectId + " option:selected")).text();
                var parsedColName = selectedCol.replaceAll('Choose Column', '');
                var colValues = col_data_parsed[parsedColName];
                updateSelectColValBox1(colValues);
            }

        });

        var updateSelectColValBox = function (colValues) {
            selectId = selectId.slice(-1);
            var colValueArray = Object.values(colValues);
            var listItems = "";
            for (var i = 0; i < colValueArray.length; i++) {
                listItems += "<option value='" + colValueArray[i] + "'>" + colValueArray[i] + "</option>";
            }
            $(("select#LCV" + selectId)).html(listItems);
        }

        let Rdropdown = $('#RCN' + clicks);
        let RdropdownVal = $('#RCV' + clicks);
        Rdropdown.empty();
        RdropdownVal.empty();
        Rdropdown.append('<option selected="true" disabled>Choose Column</option>');
        RdropdownVal.append('<option selected="true" disabled>Choose Column Value</option>');
        Rdropdown.prop('selectedIndex', 0);
        RdropdownVal.prop('selectedIndex', 0);
        // Populate dropdown with list of columns
        $.each(col_data_parsed, function (key, entry) {
            Rdropdown.append($('<option></option>').attr('value', key).text(key));
        });

        var updateSelectColValBox1 = function (colValues) {
            selectId = selectId.slice(-1);
            var colValueArray = Object.values(colValues);
            var listItems = "";
            for (var i = 0; i < colValueArray.length; i++) {
                listItems += "<option value='" + colValueArray[i] + "'>" + colValueArray[i] + "</option>";
            }
            $(("select#RCV" + selectId)).html(listItems);
        }

    });


});

function AjaxDownload(div) {
    $.ajax({
        type: 'POST',
        url: 'AjaxDownload',
        processData: false,
        contentType: "application/json",
        headers: { 'X-CSRFToken': "{{ csrf_token }}" },
        data: JSON.stringify({ 'Ldiv': div }),
        success: function (data) {
            var contentType = 'application/force-download';
            try {
                var blob = new Blob([data], { type: contentType });

                var downloadUrl = URL.createObjectURL(blob);
                var a = document.createElement("a");
                a.href = downloadUrl;
                a.download = filename;
                document.body.appendChild(a);
                a.click();

            } catch (exc) {
                console.log("Save Blob method failed with the following exception.");
                console.log(exc);
            }
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });

}

function GetAjax(FilterDataGraphL, FilterDataGraphR, Ldiv, Rdiv) {
    // if (position == "L")
    // {
    //     var FilterDataGraph = LDict;
    // }
    // if (position == "R")
    // {
    //     var FilterDataGraph = RDict;
    // }

    tempJson = { 'GraphL': FilterDataGraphL, 'GraphR': FilterDataGraphR };
    stringifyOutput = JSON.stringify(tempJson);

    $.ajax({
        type: 'POST',
        url: 'AjaxCall',
        processData: false,
        contentType: "application/json",
        headers: { 'X-CSRFToken': "{{ csrf_token }}" },
        data: JSON.stringify({ 'GraphL': FilterDataGraphL, 'GraphR': FilterDataGraphR, 'Ldiv': Ldiv, 'Rdiv': Rdiv }),
        success: function (data) {
            //alert("Success");
            //alert(data["log_attributes_L"]["dfg"]);
            CreateGraph(JSON.stringify(data["log_attributes_L"]["dfg"]), Ldiv);
            CreateGraph(JSON.stringify(data["log_attributes_R"]["dfg"]), Rdiv);
            DisplayAttributes = document.getElementById("Att" + Ldiv);
            DisplayAttributes.innerHTML = "";
            DisplayAttributes.setAttribute("style", "width: 100%;height:250px;overflow-y:scroll");
            CreateAttributeText(data["log_attributes_L"]["no_events"], data["log_attributes_R"]["no_events"], "Events", DisplayAttributes);
            CreateAttributeText(data["log_attributes_L"]["no_cases"], data["log_attributes_R"]["no_cases"], "Cases", DisplayAttributes);
            CreateAttributeText(data["log_attributes_L"]["no_variants"], data["log_attributes_R"]["no_variants"], "Number of Variants", DisplayAttributes);
            CreateAttributeText(data["log_attributes_L"]["total_case_duration"], data["log_attributes_R"]["total_case_duration"], "Total Case Duration", DisplayAttributes);
            CreateAttributeText(data["log_attributes_L"]["avg_case_duration"], data["log_attributes_R"]["avg_case_duration"], "Average Case Duration", DisplayAttributes);
            CreateAttributeText(data["log_attributes_L"]["median_case_duration"], data["log_attributes_R"]["median_case_duration"], "Median Case Duration", DisplayAttributes);
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });
}

function CreateForm(id, divElement) {

    var leftId = id;
    var rightId = id + 1;
    var br = document.createElement("br");
    // var form = document.createElement("form");
    // form.setAttribute("method", "get");
    // form.setAttribute("id", id);
    // Create an input element for ColName
    var ColNamePara = document.createElement("span");
    var ColNameText = document.createTextNode("Column Name: ");
    ColNamePara.appendChild(ColNameText);
    ColNamePara.setAttribute("style", "width: 50%;float:left;");

    var ColName = document.createElement("select");
    ColName.setAttribute("value", "Column Name");
    ColName.setAttribute("id", ('LCN' + leftId));
    ColName.setAttribute("style", "width: 50%;float:left;");


    // Create an input element for ColValue
    var ColValPara = document.createElement("span");
    var ColValueText = document.createTextNode("Column Value: ");
    ColValPara.appendChild(ColValueText);
    ColValPara.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");

    var ColVal = document.createElement("select");
    ColVal.setAttribute("value", "Column Value");
    ColVal.setAttribute("id", ('LCV' + leftId));
    ColVal.setAttribute("style", "width: 50%;float:left;");
    //
    var TypeValuePara = document.createElement("span");
    var TypeValueText = document.createTextNode("Type Value: ");
    TypeValuePara.appendChild(TypeValueText);
    TypeValuePara.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");

    var TypeValue = document.createElement("select");
    TypeValue.setAttribute("id", ('LTV' + leftId));
    for (index in Type_array) {
        TypeValue.options[TypeValue.options.length] = new Option(Type_array[index], index);
    }
    TypeValue.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");

    // Create an input element for CheckBox
    var FilterValPara = document.createElement("span");
    var FilterValText = document.createTextNode("All except this value");
    FilterValPara.appendChild(FilterValText);
    FilterValPara.setAttribute("style", "width: 45%;float:left;margin-top: 5px;");

    var FilterVal = document.createElement("input");
    FilterVal.setAttribute("type", "checkbox");
    FilterVal.setAttribute("value", "All except this Value");
    FilterVal.setAttribute("style", "width: 5%;float:left;margin-top: 5px;");
    FilterVal.setAttribute("id", ('LCB' + leftId));



    var FilterEdgesPara = document.createElement("span");
    var FilterEdgesText = document.createTextNode("Filters Edge Percentage: ");
    FilterEdgesPara.appendChild(FilterEdgesText);
    FilterEdgesPara.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");
    var FilterEdges = document.createElement("input");
    FilterEdges.setAttribute("type", "range");
    FilterEdges.setAttribute("class", "range");
    FilterEdges.setAttribute("min", 0);
    FilterEdges.setAttribute("max", 100);
    FilterEdges.setAttribute("value", 100);
    FilterEdges.setAttribute("step", 10);
    FilterEdges.setAttribute("style", "width: 45%;float:left;height:5%;");
    FilterEdges.setAttribute("oninput", "this.nextElementSibling.value = this.value");
    FilterEdges.setAttribute("id", ('LFE' + leftId));


    var FilterEdgeValue = document.createElement("output");
    FilterEdgeValue.setAttribute("style", "width: 5%;float:left;margin-top: 5px;");

    // Right Graph Filters
    var RColNamePara = document.createElement("span");
    var RColNameText = document.createTextNode("Column Name: ");
    RColNamePara.appendChild(RColNameText);
    RColNamePara.setAttribute("style", "width: 50%;float:right;");
    var RColName = document.createElement("select");
    RColName.setAttribute("value", "Column Name");
    RColName.setAttribute("id", ('RCN' + rightId));
    RColName.setAttribute("style", "width: 50%;float:right;");


    // Create an input element for ColValue
    var RColValPara = document.createElement("span");
    var RColValueText = document.createTextNode("Column Value: ");
    RColValPara.appendChild(RColValueText);
    RColValPara.setAttribute("style", "width: 50%;float:right;margin-top: 5px;");

    var RColVal = document.createElement("select");
    RColVal.setAttribute("value", "Column Value");
    RColVal.setAttribute("id", ('RCV' + rightId));
    RColVal.setAttribute("style", "width: 50%;float:right;");


    // Create an input element for CheckBox
    var RFilterValPara = document.createElement("span");
    var RFilterValText = document.createTextNode("All except this value");
    RFilterValPara.appendChild(RFilterValText);
    RFilterValPara.setAttribute("style", "width: 45%;float:right;margin-top: 5px;");

    var RFilterVal = document.createElement("input");
    RFilterVal.setAttribute("type", "checkbox");
    RFilterVal.setAttribute("value", "All except this Value");
    RFilterVal.setAttribute("style", "width: 5%;float:left;margin-top: 5px;");
    RFilterVal.setAttribute("id", ('RCB' + rightId));
    //
    var RTypeValuePara = document.createElement("span");
    var RTypeValueText = document.createTextNode("Type Value: ");
    RTypeValuePara.appendChild(RTypeValueText);
    RTypeValuePara.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");

    var RTypeValue = document.createElement("select");
    RTypeValue.setAttribute("id", ('RTV' + rightId));
    for (i in Type_array) {
        RTypeValue.options[RTypeValue.options.length] = new Option(Type_array[i], i);
    }
    RTypeValue.setAttribute("style", "width: 50%;float:left;margin-top: 5px;");

    //

    var RFilterEdgesPara = document.createElement("span");
    var RFilterEdgesText = document.createTextNode("Filters Edge Percentage: ");
    RFilterEdgesPara.appendChild(RFilterEdgesText);
    RFilterEdgesPara.setAttribute("style", "width: 50%;float:right;margin-top: 5px;");
    var RFilterEdges = document.createElement("input");
    RFilterEdges.setAttribute("type", "range");
    RFilterEdges.setAttribute("class", "range");
    RFilterEdges.setAttribute("min", 0);
    RFilterEdges.setAttribute("max", 100);
    RFilterEdges.setAttribute("value", 100);
    RFilterEdges.setAttribute("step", 10);
    RFilterEdges.setAttribute("style", "width: 45%;float:right;height:5%;");
    RFilterEdges.setAttribute("oninput", "this.nextElementSibling.value = this.value");
    RFilterEdges.setAttribute("id", ('RFE' + rightId));


    var RFilterEdgeValue = document.createElement("output");
    RFilterEdgeValue.setAttribute("style", "width: 5%;float:right;margin-top: 5px;");



    var s = document.createElement("button");
    s.setAttribute("type", "submit");
    s.innerHTML = "Compare";
    s.setAttribute("id", ('B' + clicks));
    s.setAttribute("class", "btn btn-outline-secondary");
    s.setAttribute("style", "display: block ; margin:auto;");

    var p = document.createElement("button");
    p.setAttribute("type", "submit");
    p.innerHTML = "PDF Download";
    p.setAttribute("id", ('P' + clicks));
    p.setAttribute("class", "btn btn-outline-secondary");
    p.setAttribute("style", "float:left;width:20%;height: 8%;");

    var PrintLGraph = document.createElement("button");
    PrintLGraph.setAttribute("type", "submit");
    PrintLGraph.innerHTML = "Left Graph";
    PrintLGraph.setAttribute("id", ('PrintLGraph' + clicks));
    PrintLGraph.setAttribute("class", "btn btn-outline-secondary");
    PrintLGraph.setAttribute("style", "float:left;width:20%;height: 8%;");

    var PrintRGraph = document.createElement("button");
    PrintRGraph.setAttribute("type", "submit");
    PrintRGraph.innerHTML = "Right Graph";
    PrintRGraph.setAttribute("id", ('PrintRGraph' + clicks));
    PrintRGraph.setAttribute("class", "btn btn-outline-secondary");
    PrintRGraph.setAttribute("style", "float:left;width:20%;height: 8%;");


    var Leftlog = document.createElement("button");
    Leftlog.setAttribute("type", "submit");
    Leftlog.innerHTML = "Export Left Log";
    Leftlog.setAttribute("id", ('LL' + clicks));
    Leftlog.setAttribute("class", "btn btn-outline-secondary");
    Leftlog.setAttribute("style", "float:left;width:20%;height: 8%;");

    var rightlog = document.createElement("button");
    rightlog.setAttribute("type", "submit");
    rightlog.innerHTML = "Export Right Log";
    rightlog.setAttribute("id", ('RL' + clicks));
    rightlog.setAttribute("class", "btn btn-outline-secondary");
    rightlog.setAttribute("style", "float:left;width:20%;height: 8%;");

    divElement.appendChild(ColNamePara);
    divElement.appendChild(RColNamePara);
    //divElement.appendChild(br.cloneNode());
    divElement.appendChild(ColName);
    divElement.appendChild(RColName);
    divElement.appendChild(br.cloneNode());

    divElement.appendChild(ColValPara);
    divElement.appendChild(RColValPara);
    //divElement.appendChild(br.cloneNode());
    divElement.appendChild(ColVal);
    divElement.appendChild(RColVal);
    divElement.appendChild(br.cloneNode());

    divElement.appendChild(FilterVal);
    divElement.appendChild(FilterValPara);
    divElement.appendChild(RFilterVal);
    divElement.appendChild(RFilterValPara);
    divElement.appendChild(br.cloneNode());

    divElement.appendChild(TypeValuePara);
    divElement.appendChild(RTypeValuePara);
    divElement.appendChild(br.cloneNode());
    divElement.appendChild(TypeValue);
    divElement.appendChild(RTypeValue);
    divElement.appendChild(br.cloneNode());

    divElement.appendChild(FilterEdgesPara);
    divElement.appendChild(RFilterEdgesPara);
    divElement.appendChild(br.cloneNode());
    divElement.appendChild(FilterEdges);
    divElement.appendChild(FilterEdgeValue);
    divElement.appendChild(RFilterEdges);
    divElement.appendChild(RFilterEdgeValue);
    divElement.appendChild(br.cloneNode());

    divElement.appendChild(s);
    divElement.appendChild(br.cloneNode());
    divElement.appendChild(Leftlog);
    divElement.appendChild(PrintLGraph);
    divElement.appendChild(p);
    divElement.appendChild(PrintRGraph);
    divElement.appendChild(rightlog);
    // divElement.appendChild(form);

    divElement.appendChild(br.cloneNode());
    ShowAttributes(divElement);
}

function CreateAttributeText(LValue, RValue, AttributeName, divElement) {
    var br = document.createElement("br");
    var Event = document.createElement("h4");
    var EventText = document.createTextNode(AttributeName);
    Event.setAttribute("style", "width: 100%;color:grey;text-align:center;float:left");
    var LEvents = document.createElement("h4");
    var LEventsText = document.createTextNode(LValue);
    LEvents.setAttribute("style", "width: 45%;float:left;color:green;text-align:center");
    var REvents = document.createElement("h4");
    var REventsText = document.createTextNode(RValue);
    REvents.setAttribute("style", "width: 45%;float:right;color:green;text-align:center");
    var VS = document.createElement("p");
    var VSText = document.createTextNode("VS");
    VS.setAttribute("style", "width: 10%;float:left;color:grey;text-align:center");


    VS.appendChild(VSText);
    divElement.appendChild(Event);
    Event.appendChild(EventText);
    LEvents.appendChild(LEventsText);
    REvents.appendChild(REventsText);
    divElement.appendChild(LEvents);
    divElement.appendChild(VS);
    divElement.appendChild(REvents);
    divElement.appendChild(br.cloneNode());
}

function printDiv(Lgraph, Rgraph) {

    var LgraphDiv = document.getElementById(Lgraph).firstElementChild.toDataURL();
    var centerDiv = document.getElementById("Att" + Lgraph).innerHTML;
    var RgraphDiv = document.getElementById(Rgraph).firstElementChild.toDataURL();
    var htmlToPrint = '' +
        '<style type="text/css">' +
        'height:300px' +
        'border:1px solid #000;' +
        'padding;0.5em;' +
        'width:20%' +
        '</style>';


    htmlToPrint += centerDiv.innerHTML;
    const a = window.open('', '', 'width=600,height=650');
    a.document.open();
    a.document.write('<html>');
    a.document.write('<body>');
    a.document.write('<div>');
    a.document.write('<img src="' + LgraphDiv + '" style="height:450px;width:35%;float:left;">');
    a.document.write('<div style="height:50%;width:30%;float:left;"> "' + centerDiv + '"</div>');
    a.document.write('<img src="' + RgraphDiv + '" style="height:450px;width:35%;float:right;">');
    a.document.write('</div>');
    a.document.write('</body></html>');
    a.document.close();
    a.document.addEventListener('DOMContentLoaded', function () {
        a.focus();
        a.print();
        a.close();
    }, true);

}

function GetFormValues(id, position) {
    if (position == "R") {
        RDict["FileName"] = filename;
        RDict["ColumnName"] = $(("select#" + ("RCN" + id) + " option:selected")).text();
        RDict["ColumnValue"] = $(("select#" + ("RCV" + id) + " option:selected")).text();
        RDict["Checkbox"] = document.getElementById(("RCB" + id)).checked;
        RDict["Type"] = $(("select#" + ("RTV" + id) + " option:selected")).text();
        RDict["FilterPercentage"] = document.getElementById(("RFE" + id)).value;
    }
    if (position == "L") {
        LDict["FileName"] = filename;
        LDict["ColumnName"] = $(("select#" + ("LCN" + id) + " option:selected")).text();
        LDict["ColumnValue"] = $(("select#" + ("LCV" + id) + " option:selected")).text();
        LDict["Checkbox"] = document.getElementById(("LCB" + id)).checked;
        LDict["Type"] = $(("select#" + ("LTV" + id) + " option:selected")).text();
        LDict["FilterPercentage"] = document.getElementById(("LFE" + id)).value;

    }
}

function ShowAttributes(divElement) {
    var br = document.createElement("br");
    Events = "{{log_attributes.no_events}}";
    Cases = "{{log_attributes.no_cases}}";
    no_variants = "{{log_attributes.no_variants}}";
    total_case_duration = "{{log_attributes.total_case_duration}}";
    avg_case_duration = "{{log_attributes.avg_case_duration}}";
    median_case_duration = "{{log_attributes.median_case_duration}}";


    var DisplayAttributes = document.createElement("Div");
    DisplayAttributes.setAttribute("style", "width: 100%;height:250px;overflow-y:scroll");
    DisplayAttributes.setAttribute("id", "Att" + clicks);

    divElement.appendChild(DisplayAttributes);

    CreateAttributeText(Events, Events, "Events", DisplayAttributes);
    CreateAttributeText(Cases, Cases, "Cases", DisplayAttributes);
    CreateAttributeText(no_variants, no_variants, "Number of Variants", DisplayAttributes);
    CreateAttributeText(total_case_duration, total_case_duration, "Total Case Duration", DisplayAttributes);
    CreateAttributeText(avg_case_duration, avg_case_duration, "Average Case Duration", DisplayAttributes);
    CreateAttributeText(median_case_duration, median_case_duration, "Median Case Duration", DisplayAttributes);

}

function AddModel1(data) {
    filename = "{{ log_name}}"
    clicks += 1;
    var leftDivId = clicks;
    // create a new div element
    const leftDiv = document.createElement("div");
    leftDiv.setAttribute("id", leftDivId);
    leftDiv.setAttribute("style", "border : 1px solid #000000; height: 750px; width: 35%;float:left;");
    const currentDiv = document.getElementById("DisplayGraph");
    const Duplicatediv = document.getElementById("GetFiltersDiv");
    const centerDiv = Duplicatediv.cloneNode(true);
    centerDiv.setAttribute("id", ('Div' + clicks));
    centerDiv.setAttribute("style", "border : 1px solid #000000; height: 750px; width: 30%;float:left;");
    CreateForm(clicks, centerDiv);
    const rightDiv = document.createElement("div");
    clicks += 1;
    var rightDivId = clicks;
    rightDiv.setAttribute("id", rightDivId);
    rightDiv.setAttribute("style", "border : 1px solid #000000; height: 750px; width: 35%;float:left;");

    currentDiv.appendChild(leftDiv);
    currentDiv.appendChild(centerDiv);
    currentDiv.appendChild(rightDiv);

    CreateGraph(data, leftDivId);
    CreateGraph(data, rightDivId);
    rangeInput();
}

function nodecolFunc(node) {
    if (node.isUnique === 'True')
        return '#FF0000';
    return '#C6E5FF';
}

function CreateGraph(JObj, id) {
    const container = document.getElementById(id);
    const width = container.scrollWidth || 500;
    const height = container.scrollHeight || 500;
    const graph = new G6.Graph({
        container,
        width,
        height,
        layout: {
            type: 'dagre',
            nodesepFunc: (d) => {
                if (d.id === '3') {
                    return 500;
                }
                return 50;
            },
            ranksep: 70,
            controlPoints: true,
        },
        defaultNode: {
            type: 'sql',
        },
        defaultEdge: {
            type: 'polyline',
            style: {
                radius: 20,
                offset: 45,
                endArrow: true,
                lineWidth: 2,
                stroke: '#C2C8D5',
            },
            labelCfg: {
                style: {
                    fontSize: 25,
                    fontWeight: "bold"
                }
            },
        },
        nodeStateStyles: {
            selected: {
                stroke: '#d9d9d9',
                fill: '#5394ef',
            },
        },
        modes: {
            default: [
                'drag-canvas',
                'zoom-canvas',
                'click-select',
                'drag-node',
                {
                    type: 'tooltip',
                    formatText(model) {
                        const cfg = model.conf;
                        const text = [];
                        cfg.forEach((row) => {
                            text.push(row.label + ':' + row.value + '<br>');
                        });
                        return text.join('\n');
                    },
                    offset: 30,
                },
            ],
        },
        fitView: true,
    });

    G6.registerNode(
        'sql',
        {
            drawShape(cfg, group) {
                const rect = group.addShape('rect', {
                    attrs: {
                        x: -75,
                        y: -25,
                        width: 150,
                        height: 50,
                        radius: 10,
                        stroke: '#5B8FF9',
                        fill: nodecolFunc(cfg),
                        lineWidth: 3,
                    },
                    name: 'rect-shape',
                });
                if (cfg.name) {
                    group.addShape('text', {
                        attrs: {
                            text: cfg.name,
                            x: 0,
                            y: 0,
                            fill: '#00287E',
                            fontSize: 14,
                            textAlign: 'center',
                            textBaseline: 'middle',
                            fontWeight: 'bold',
                        },
                        name: 'text-shape',
                    });
                }
                return rect;
            },
        },
        'single-node',
    );
    console.log('foo was there')
    //var var_data = "{{v}}";
    var_data_parsed = JSON.parse(JObj.replace(/&quot;/g, '"'));
    graph.data(var_data_parsed);
    graph.render();

    if (typeof window !== 'undefined')
        window.onresize = () => {
            if (!graph || graph.get('destroyed')) return;
            if (!container || !container.scrollWidth || !container.scrollHeight) return;
            graph.changeSize(container.scrollWidth, container.scrollHeight);
        };


}

function rangeInput() {
    const allRanges = document.querySelectorAll(".range-wrap");
    allRanges.forEach(wrap => {
        const range = wrap.querySelector(".range");
        const bubble = wrap.querySelector(".bubble");

        range.addEventListener("input", () => {
            console.log("event listerner input kay andar hu may");
            setBubble(range, bubble);
        });
        console.log("foofoofoo");
        setBubble(range, bubble);
    });
}
function setBubble(range, bubble) {
    console.log("setBubble Call hua hai");
    const val = range.value;
    const min = range.min ? range.min : 0;
    const max = range.max ? range.max : 100;
    const newVal = Number(((val - min) * 100) / (max - min));
    bubble.innerHTML = val;

    // Sorta magic numbers based on size of the native UI thumb
    bubble.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`;
}