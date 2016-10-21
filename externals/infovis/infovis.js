
window.cy = null;
window.$  = jQuery;

window.gs = null; //galaxy summary
window.cg = null; //custom graph
window.custom_graph_data = {};
window.universe          = {
    "nodecount"     : 0,
    "categories"    : []
};

/**
    Given a sentiment string, returns an adequate color.

    @date 20160408
    @author Daniel Cantarín
*/

function exportToCsv(filename, rows) {
        var processRow = function (row) {
            var finalVal = '';
            for (var j = 0; j < row.length; j++) {
                var innerValue = row[j] === null ? '' : row[j].toString();
                if (row[j] instanceof Date) {
                    innerValue = row[j].toLocaleString();
                };
                var result = innerValue.replace(/"/g, '""');
                if (result.search(/("|,|\n)/g) >= 0)
                    result = '"' + result + '"';
                if (j > 0)
                    finalVal += ',';
                finalVal += result;
            }
            return finalVal + '\n';
        };

        var csvFile = '';
        for (var i = 0; i < rows.length; i++) {
            csvFile += processRow(rows[i]);
        }

        var blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
        if (navigator.msSaveBlob) { // IE 10+
            navigator.msSaveBlob(blob, filename);
        } else {
            var link = document.createElement("a");
            if (link.download !== undefined) { // feature detection
                // Browsers that support HTML5 download attribute
                var url = URL.createObjectURL(blob);
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
    }

function exportCSV() {
    //console.log("0000000000")
    custom_graph_data = JSON.parse( $("svg > #graph-data").text() );
    csvRows = [["id", "title", "url", "categories", "source", "date", "sentiment", "children"]]
    //console.log(custom_graph_data)
    for (a_key in custom_graph_data){
            a_node = custom_graph_data[a_key]
            scored_children = []
            for (i = 0; i < a_node["children"].length; i++) {
                scored_children.push({"id": a_node["children"][i], "score": a_node["scores"][i]})
            }
            csvRows.push([a_node["oid"], a_node["title"], a_node["url"], JSON.stringify(a_node["cats"]), a_node["source"], a_node["date"], a_node["sentiment"], JSON.stringify(scored_children)])
            //console.log(custom_graph_data[a_key])
    }
    //console.log(csvRows)
    exportToCsv("universe.csv", csvRows)
}

function color_by_sentiment( sent ) {
    var white = "#ffffff";
    var red   = "#ff0000";
    var green = "#00ff00";

    var ret = white;

    if ( sent === undefined || sent === null || sent.trim() == "") {
        sent = "neutral";
    }

    sent = sent.toLowerCase();

    if ( sent.indexOf("negative") > -1 ) {
        ret = red;
    } else if ( sent.indexOf("positive") > -1) {
        ret = green;
    }
    //console.log("color_by_sentiment", sent, ret);

    return ret;
}

/**
    Given a sentiment string, returns an adequate opacity.

    @date 20160408
    @author Daniel Cantarín
*/
function opacity_by_sentiment( sent ) {
    var very        = "1";
    var slightly    = "0.15";
    var normal      = "0.5";

    var ret = normal;

    if ( sent === undefined || sent === null ) {
        sent = "neutral";
    }

    sent = sent.toLowerCase();

    if ( sent.indexOf("very") > -1 ) {
        ret = very;
    } else if ( sent.indexOf("slightly") > -1) {
        ret = slightly;
    }
    //console.log("opacity_by_sentiment", sent, ret);

    return ret;
}

function random_color() {
    var red     = parseInt(Math.random() * 255);
    var green   = parseInt(Math.random() * 255);
    var blue    = parseInt(Math.random() * 255);
    var color   = "#" + red.toString(16) + green.toString(16) + blue.toString(16);

    while (color.length < 7) {
        color += "0";
    }

    //color = "rgba(" + red + "," + green + "," + blue + "," + Math.random().toString().substring(0,4) + ")";

    return color;
}


function process_json_new( obj ) {
        //LEGACY MODE:
        if(obj.root !== undefined){
            return process_json(obj);
        }

        //NEW MODE:
        var nodes = [];

        //NODES:
        var node_index = 0;
        while(obj[node_index] !== undefined){
                node_object = obj[node_index];

                if(node_object.title.length > 25){
                    node_object.title_small = node_object.title.substring(0,22) + "...";
                }else{
                    node_object.title_small = node_object.title;
                }

                node_object.mongo_id = node_object.id;
                node_object.id      = node_index.toString();

                //VALUES FOR NODE COLOR:
                node_object.color   = color_by_sentiment(node_object.sentiment);

                //VALUES FOR NODE SIZE:
                var children_size = 1;
                if(node_object.edges){

                    children_size = node_object.edges.length + 1;

                }


                var children_multiplier = 0;
                if(node_object.level == 0){            //ONLY ROOT PARAMETERS:

                    node_object.root = true;
                    children_multiplier = 30;
                    children_size--;

                }else if(node_object.level == 1 || node_object.level == 2){    //ONLY SECOND AND THIRD GENERATION:
                    children_multiplier = 20;
                }

                //COMPATIBILITY ONLY:
                node_object["index"] = node_object["level"];
                node_object["children"] = node_object.edges;

                final_node = {
                            "group": "nodes",
                            "data" : node_object,
                            "index": nodes.length +1,
                        };
                if(node_object.level <= 2){
                    final_node["style"] = {
                        "width"             : children_size * children_multiplier,
                        "height"            : children_size * children_multiplier,
                    };
                }

                nodes.push(final_node);

                node_index++;
        }

        var nodecount = node_index;

        //EDGES:
        var node_index = 0;
        while(obj[node_index] !== undefined){
                node_object = obj[node_index];

                for(var i = 0; i < node_object.edges.length; i++){
                        nodes.push({
                                "group"       : "edges",
                                "data"        :{
                                    "id"        : node_index.toString() + "-" + node_object.edges[i].toString(),
                                    "source"    : node_index.toString(),
                                    "target"    : node_object.edges[i].toString(),
                                    "width"     : 30 / (node_object["level"]+1),
                                },
                        });
                }
                node_index++;
        }


        window.nodeset = {
            "nodes"     : nodes,
            "nodecount" : nodecount
        };

        return {
            "nodes" : nodes
        };
}


/**
    Given a JSON object, it creates the required structure for
    graphic libraries to render.

    @date 20160323
    @author Daniel Cantarín
*/
function process_json( obj ) {

    var nodecount = 0;

    obj.root.root = true;
    title = obj.root.title
    obj.root.title_small = (title.length > 25)
        ? title.substring(0,22) + "..."
        : title;

    obj.root.color      = color_by_sentiment(obj.root.sentiment);
    obj.root.opacity    = opacity_by_sentiment(obj.root.sentiment);
    var color           = random_color();
    //obj.root.border     = color;

    var nodes   = [ {
        "data" : obj.root,
        "css"  : {
            "width" : obj.root.children.length * 30,
            "height": obj.root.children.length * 30
        }
    }];
    var i       = 0;

    // Hijos de root
    for ( i = 0; i < obj.root.children.length; i++ ) {
        var tmp         = obj.root.children[i];
        tmp.color       = color_by_sentiment(tmp.sentiment);
        tmp.opacity     = opacity_by_sentiment(tmp.sentiment);
        tmp.index = 1;
        tmp.title_small = (tmp.title.length > 25)
            ? tmp.title.substring(0,22) + "..."
            : tmp.title;
        var len     =   (tmp.children)
                    ?   tmp.children.length + 1
                    :   1;

        nodes.push( {
            "data" : tmp,
            "css"  : {
                "width" : len * 20,
                "height": len * 20
            }
        });
        nodes.push( { "data" : {
            "id"        : obj.root.id + tmp.id,
            "source"    : obj.root.id,
            "target"    : tmp.id,
            "color"     : color,
            "union"     : true,
            "width"     : 30 / tmp.index
        } } );
    }

    // Nietos de root
    for ( i = 1; i < nodes.length; i++ ) {
        var tmp  = nodes[i];
        if (tmp.data.children !== undefined) {
            //console.log(tmp.data.title + " :" + tmp.data.children.length + " hijos.");
            color = random_color();
            for ( var i2 = 0; i2 < tmp.data.children.length; i2++ ) {
                var tmp2 = tmp.data.children[i2];
                tmp2.index = 2;
                tmp2.color       = color_by_sentiment(tmp2.sentiment);
                //tmp2.border      = color;
                tmp2.opacity     = opacity_by_sentiment(tmp2.sentiment);
                tmp2.title_small = (tmp2.title.length > 25)
                    ? tmp2.title.substring(0,22) + "..."
                    : tmp2.title;

                var len     =   (tmp2.children)
                            ?   tmp2.children.length + 1
                            :   1;
                nodes.push( {
                    "data" : tmp2,
                    "css"  : {
                        "width" : len * 20,
                        "height": len * 20
                    }
                });
                nodes.push( { "data" : {
                    "id"        : tmp.data.id + tmp2.id,
                    "source"    : tmp.data.id,
                    "target"    : tmp2.id,
                    "color"     : color,
                    "union"     : true,
                    "width"     : 30 / tmp2.index
                } } );

                // Bisnietos de root
                if (tmp2.children) {
                    for ( var i3 = 0; i3 < tmp2.children.length; i3++ ) {
                        color           = random_color();
                        var tmp3        = tmp2.children[i3];
                        tmp3.index      = 3;
                        //tmp3.border     = color;
                        tmp3.color      = color_by_sentiment(tmp3.sentiment);
                        tmp3.opacity    = opacity_by_sentiment(tmp3.sentiment);
                        tmp3.title_small = (tmp3.title.length > 25)
                            ? tmp3.title.substring(0,22) + "..."
                            : tmp3.title;
                        nodes.push( { "data" : tmp3 });
                        nodes.push( { "data" : {
                            "id"        : tmp2.id + tmp3.id,
                            "source"    : tmp2.id,
                            "target"    : tmp3.id,
                            "color"     : color,
                            "union"     : true,
                            "width"     : 30 / tmp3.index
                        } } );
                    }
                } else {
                    //console.log("tmp2 no tiene hijos" , tmp2);
                }
            }
        }
    }

    var urls = [];
    for (var i = 0; i < nodes.length; i++){
        if ( nodes[i].data && nodes[i].data.union === undefined) {
            if ( urls.indexOf( nodes[i].data.url ) < 0 ) {
                urls.push( nodes[i].data.url );
                nodecount++;
                nodes[i].index = nodecount;
            }
        }
    }

    window.nodeset = {
        "nodes"     : nodes,
        "nodecount" : nodecount
    };

    return {
        "nodes" : nodes
    };
}

function show_data_overlay( obj ){

    var cities      = (obj.geo !== null && obj.geo.cities !== null && obj.geo.cities instanceof Array)
                    ? array_to_divs(obj.geo.cities , "tag-styled")
                    : "";

    var countries   = (obj.geo !== null && obj.geo.countries !== null && obj.geo.countries instanceof Array)
                    ? array_to_divs(obj.geo.countries , "tag-styled")
                    : "";

    var categories  = (obj.categories !== null && obj.categories instanceof Array)
                    ? array_to_divs( obj.categories, "tag-styled")
                    : "";

    var tags        = (obj.tags !== null && obj.tags instanceof Array)
                    ? array_to_divs(obj.tags, "tag-styled")
                    : "";

    var url         = (obj.wp_url !== null && obj.wp_url !== undefined)
                    ? obj.wp_url
                    : obj.url;

    $("#title-news").html( obj.title );
    $("#cities .value").html( cities );
    $("#countries .value").html( countries );
    $("#categories .value").html( categories );
    $("#tags .value").html( tags );
    $("#sentiment .value").html( "<div class=\"tag-styled\">" + ((obj.sentiment !== null) ? obj.sentiment : "&nbsp;") +"</div>");
    $("#date .value").html( "<div class=\"tag-styled\">" + ((obj.date !== "None" && obj.date !== null) ? obj.date.split(".")[0] : "&nbsp;") + "</div>");
    $("#source .value").html( "<div class=\"tag-styled\">" + ((obj.source !== null) ? obj.source : "&nbsp;") + "</div>");
    $("#summary .value").html( "<div class=\"summary\">" + ((obj.summary !== null) ? obj.summary : "&nbsp;") + "</div>");
    $("#url .value").html( "<div class=\"tag-styled\" style=\"overflow-x:auto;\"><a href=\"" + url + "\" target=\"_blank\">" + url + "</a></div>" );
    $("#leyenda, #stats, #powered-by, #titulo-noticia, #visualizaciones, #download").hide(100);
    $("#data-overlay").slideDown(500);
}

function array_to_divs( arr , styles) {
    var ret = "";

    for (var i = 0; i < arr.length; i++) {
        if (arr[i] === undefined || arr[i] === null) {
            continue;
        }
        ret += "<div ";
        if (styles !== undefined) {
            ret += "class=\"" + styles + "\" ";
        }
        ret += ">" + arr[i] + "</div>";
    }

    return ret;
}

function hide_data_overlay() {
    $("#data-overlay").slideUp(250).promise().then(
        function() {
            $("#leyenda, #stats, #powered-by, #visualizaciones, #download").show(500);
        }
    );
}

function center_cy() {
    cy.$("node").unselect();
    cy.animate({
        center: { eles: cy.$("node[root]") },
        zoom : 0.5
    });
}

function mostrar_titulo( titulo, fecha ) {
    html = "<h4>" + titulo;
    if (fecha !== undefined && fecha !== null && fecha !== "None") {
        html += "<br/>date : " + fecha.split(".")[0];
    }
    $("#titulo-noticia").html( html +  "</h4>" ).fadeIn(500);
}

function ocultar_titulo() {
    $("#titulo-noticia").fadeOut(250);
}

function setup_cy() {



    var tmp_resize = function() {
        $("#cy")
        .css("width", $(document).width() + "px")
        .css("height",$(document).height() + "px");

        if (window.cy != null) {
            console.log("cy not null");
            window.setTimeout(10,window.cy.resize);
        } else {
            console.log("cy es null");
        }
    }
    tmp_resize();

    $("#data-overlay").hide();

    window.cy = cytoscape({
        wheelSensitivity: 0.1,
        container: document.getElementById('cy'), // container to render in
        elements: process_json_new( galaxy_json ).nodes,
        style: [ // the stylesheet for the graph
            {
          selector: 'node',
          style: {
            'background-color': 'data(color)',
            //'background-opacity': 'data(opacity)',
            //'border-width': '10px',
            //'border-color': 'data(border)',
            'border-width': '1px',
            'border-color': 'black',
            'shadow-color'  : 'black',
            'shadow-opacity' : '0.8',
            'shadow-offset-x' : '-2',
            'shadow-offset-y' : '2',
            'label': 'data(title_small)'
          }
        },
        {
          selector: 'node[root]',
          style: {
            /*'width'  : 100,
            'height' : 100,
            'background-color': 'red',
            'label': 'data(title_small)'*/
            'border-width': '10px',
            'background-image' : 'selected.png'
          }
        },
        {
          selector: 'node[index=1]',
          style: {
            'width'  : 'data(children.length) * 10',
            'height' : 'data(children.length) * 10'
          }
        },
        {
          selector: 'node[index>1]',
          style: {
            'width'  : 'data(index) * 100',
            'height' : 'date(index) * 100'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            //'line-color': 'data(color)',
            'line-color': 'blue',
            'opacity' : '0.6',
            'target-arrow-color': 'black',
            'target-arrow-shape': 'triangle',
            //'line-style' : 'dotted',
            'source-arrow-shape': 'circle',
            'source-arrow-color': 'black'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'line-color': '#E4860D',
            'line-weight': 3
          }
        },
        {
            selector : ':active',
            style: {
                'line-color': '#E4860D',
                'line-style': 'solid',
                'overlay-color': '#c0c0c0',
                //'overlay-padding': '100px',
                'overlay-opacity': 100
            }
        }
        ],
        layout: {
            name: 'concentric',
            concentric: function( node ){
                return node.degree();
            },
            levelWidth: function( nodes ){
                return 2;
            }
        }

    });

    cy.on("click","node", function(evt) {
        console.log(evt.cyTarget.data().color);
        var j = cy.$("#" + evt.cyTarget.data().id);
        j.select();
        //cy.center( j , 500);
        cy.animate({
            fit: { eles: "#" + evt.cyTarget.data().id }
        });
        show_data_overlay(evt.cyTarget.data());
    });

    /*
    cy.on("click", function(evt) {
        //chequeo que no esté haciendo click en algún elemento de cy.
        if ( evt.cyTarget[0] === undefined ) {
            center_cy();
            hide_data_overlay();
        }
    });
    */

    cy.on("mouseover","node", function(evt) {
        if (evt.originalEvent.target && !evt.originalEvent.target.classList.contains("mouseover")) {
            evt.originalEvent.target.classList.add("mouseover");
            var edges = evt.cyTarget.connectedEdges();
            edges.css("line-style", "solid");
            edges.css("line-color", "black");
            edges.css("opacity", "1");

            var vecinos = evt.cyTarget.neighborhood();
            var demas = cy.elements().difference( vecinos );
            demas.css("opacity", "0.3");
            evt.cyTarget.css("opacity", "1");

            mostrar_titulo( evt.cyTarget.data().title, evt.cyTarget.data().date );

        }
    });

    cy.on("mouseout","node", function(evt) {
        if (evt.originalEvent.target && evt.originalEvent.target.classList.contains("mouseover")) {
            evt.originalEvent.target.classList.remove("mouseover");
            var edges = evt.cyTarget.connectedEdges();
            //edges.css("line-style", "dotted");
            edges.css("line-color", "blue");

            //var vecinos = evt.cyTarget.neighborhood();
            //var demas = cy.elements().difference( vecinos );
            //demas.css("opacity", "1");
            cy.elements("node").css("opacity", "1")
            cy.elements("edge").css("opacity", "0.6")

            ocultar_titulo();
        }
    });

    var tmphtml = "\n<div id=\"cy-node-list\" class=\"node-list\">\
                    <div class=\"cerrar\" onclick=\"toggle_node_list();\"> X </div>\
                    <div><h2>NewsGalaxy Node List.</h2></div>\
                    <div><h3 style=\"color:red;\"> (press \"L\" key to show/hide this list) </h3></div>\
                    <table>\
                        <thead>\
                            <tr>\
                                <th>nodo</th>\
                                <th>fecha</th>\
                                <th>titulo</th>\
                            </tr>\
                        </thead>\
                        <tbody>";
    for (var i = 0; i < nodeset.nodes.length; i++) {
        if (nodeset.nodes[i].index !== undefined ) {
            tmphtml += "<tr><td>#" + nodeset.nodes[i].index + "</td><td>" + nodeset.nodes[i].data.date + "</td><td><a class=\"hoverable\" target=\"_blank\" href=\""+nodeset.nodes[i].data.url+"\">" + nodeset.nodes[i].data.title + "</a></td></tr>";
        }
    }
    tmphtml += "</tbody></table></div>";
    local_cy = $("#cy");
    local_cy.append( tmphtml );

    $(window).on(
        "resize", tmp_resize
    ).on(
        "keyup" , function(evt) {

            // Si se presiona "escape" y el overlay está visible
            if (evt.keyCode == 27 && $("#data-overlay")[0].offsetParent !== null) {
                center_cy();
                hide_data_overlay();
            } else if (evt.keyCode == 76) {
                // Tecla "L", para la lista en NewsUniverse
                if ( $(".node-list").length > 0 ) {
                    toggle_node_list();
                }
            }

        }
    );

    $("#close-overlay").on("click", function(){
        center_cy();
        hide_data_overlay();
    });


    $("#loading-overlay").fadeOut(1000);
    nodeset.leyenda_html = $("#leyenda").html();
    $("#stats #nodecount").html( nodeset.nodecount );
    $("#stats h4").html("News (nodes) arranged around the Galaxy");
}

wc = null;

function setup_wordcloud( arr ) {
    var options = {
        list : arr,
        gridSize: 18,
        weightFactor: 8,
        fontFamily: 'dosisbook',
        color:"#009",
        backgroundColor: '#fff',
        minSize: 10
    };
    wc = WordCloud("wc", options);

}

function show_wordcloud(obj) {
    $("#cy, #gs, #cg").fadeOut(100);
    select_graph_UI(obj);

    if (wc === null) {

        //cargar los datos
        $("#wc").css("cursor","wait").show(100);

        // primero junto los ids de nodos
        var nodos = cy.nodes();
        var ids   = [];
        for (var i = 0; i < nodos.length; i++) {
            if(nodos[i].data().mongo_id !== undefined){
                ids.push( nodos[i].data().mongo_id );
            }else{
                ids.push( nodos[i].data().id );
            }
        }

        $.get(
            location.protocol + "//" + location.host + "/get_cloud_data.php?news_id=" + wp_id + "&related_ids=" + ids.join(",")
        ).promise().then(
            function (resp, status, xhr) {
                //console.log(resp,status,xhr);
                if (resp.status === "success") {
                    topic_arr = resp.data.cloud_data;
                    var tmp = function() {setup_wordcloud(topic_arr); $("#wc").css("cursor","default");};
                    setTimeout(tmp,200);
                } else {
                    var message = resp.data.message;
                    alert("error leyendo datos de la topic cloud:\n" + message);
                }
            }
        );

    } else {
        $("#wc").fadeIn(500);
    }

}

function show_galaxy(obj) {
    $("#wc, #gs, #cg").fadeOut(100);
    select_graph_UI(obj);
    $("#cy").fadeIn(500).promise().then(
        function() {
            $("#stats #nodecount").html( nodeset.nodecount );
            $("#stats h4").html("News (nodes) arranged around the Galaxy");
            $("#leyenda").html( nodeset.leyenda_html );
        }
    );


}


function setup_galaxysummary() {
    if (cy !== null && cy !== undefined) {
        var tmpnod  = cy.nodes();
        var nodos   = [];

        for (var i = 0; i < tmpnod.length; i++) {
            nodos.push( {
                "title"     :   tmpnod[i].data().title,
                "date"      :   tmpnod[i].data().date,
                "summary"   :   tmpnod[i].data().summary,
                "id"        :   tmpnod[i].data().id,
                "scored_summary_clauses": tmpnod[i].data().scored_summary_clauses
            } );
        }

        var tmphtml = "";
        var sorter  = function (a, b){
            var aName = a.date;
            var bName = b.date;
            return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
        }

        nodos.sort( sorter );

        var font_colors = [
                                "red",
                                "darkviolet",
                                "orange",
                                "green",
                                "blue",
                                "fuchsia",
                                "darkred",
                                "gold",
                                "gray",
                                //"mediumvioletred",
                                "teal",
        ];

        for (var i = 0; i < nodos.length; i++) {
            tmp      = "<div class=\"news-number\"> #" + (i+1) + "&nbsp;&nbsp;</div><div class=\"title\" objectid=\"" + nodos[i].id + "\"  ><span class=\"date\">(" + nodos[i].date.split(".")[0] + ")</span> - " + nodos[i].title + "</div>\n";

            if(nodos[i].scored_summary_clauses === undefined){
                tmp     += "<div class=\"summary\">" + nodos[i].summary + "</div>";
            }else{
                tmp     += "<div class=\"summary\">";
                for(var j = 0; j < nodos[i].scored_summary_clauses.length; j++){
                    if(nodos[i].scored_summary_clauses[j]["group"] !== undefined && nodos[i].scored_summary_clauses[j]["group"] > 0){
                        color_group = nodos[i].scored_summary_clauses[j]["group"] % font_colors.length;
                        extra_tags_open = "";
                        extra_tags_close = "";
                        if(nodos[i].scored_summary_clauses[j]["group"] > font_colors.length){
                                extra_tags_open += "<u>";
                                extra_tags_close += "</u>";
                        }else if(nodos[i].scored_summary_clauses[j]["group"] > 2*font_colors.length){
                                extra_tags_open = "<i>" + extra_tags_open;
                                extra_tags_close += "</i>";
                        }else if(nodos[i].scored_summary_clauses[j]["group"] > 3*font_colors.length){
                                extra_tags_open = "<b>" + extra_tags_open;
                                extra_tags_close += "</b>";
                        }
                        tmp     += '<font color="'+ font_colors[color_group] + '">';
                        tmp     += extra_tags_open;
                        tmp     += nodos[i].scored_summary_clauses[j]["text"];
                        tmp     += extra_tags_close;
                        tmp     += '</font>';
                    }else{
                        tmp     += nodos[i].scored_summary_clauses[j]["text"];
                    }
                    //tmp     += "&nbsp";
                    tmp     += "<br>";
                }
                tmp     += "</div>";
            }


            tmphtml += tmp;
        }

        gs = tmphtml;
        $("#gs").html( tmphtml );

    }
}


function show_galaxysummary(obj) {
    $("#cy, #wc, #cg").fadeOut(100);
    select_graph_UI(obj);

    if (gs === null || gs === undefined) {
        //setup
        $("#gs").css("cursor","wait").show(100);
        setup_galaxysummary();
        $("#gs").css("cursor","default");

    } else {
        $("#gs").fadeIn(500);
    }

}


function setup_customgraph() {
    if (cy !== null && cy !== undefined) {
        /*
        #layout  = g.layout_kamada_kawai(maxiter=100) # ~3mins in eeepc (1.6 GHz dual core Atom)
        #layout  = g.layout_kamada_kawai(maxiter=1000) # ~2mins in 3.0 GHz 8-core i7
        #layout  = g.layout_kamada_kawai(maxiter=2000) # ~4mins in 3.0 GHz 8-core i7
        #layout  = g.layout_kamada_kawai(maxiter=20000) # ~34mins in 3.0 GHz 8-core i7
        #layout  = g.layout_grid_fruchterman_reingold() # ~5secs in eeepc (1.6 GHz dual core Atom)
        #layout  = g.layout_fruchterman_reingold() # ~40secs in 3.0 GHz 8-core i7
        #layout  = g.layout_reingold_tilford_circular() # ~0.1ms in 3.0 GHz 8-core i7
        #layout  = g.layout_circle() # ~3secs in eeepc (1.6 GHz dual core Atom)
        #layout  = g.layout_drl() # ~1min in eeepc (1.6 GHz dual core Atom)
        #layout  = g.layout_lgl() # ~1min in eeepc (1.6 GHz dual core Atom)
        #layout  = g.layout_random() # ~2secs in 3.0 GHz 8-core i7
        #layout  = g.layout_graphopt() # ~40secs in 3.0 GHz 8-core i7
        #layout  = g.layout_reingold_tilford() # ~2ms in 3.0 GHz 8-core i7
        #layout  = g.layout_reingold_tilford_circular() # ~3ms in 3.0 GHz 8-core i7
        #layout  = g.layout_sugiyama() # ~9ms in 3.0 GHz 8-core i7
        #layout  = g.layout_mds() # ~15secs in 3.0 GHz 8-core i7
        #layout  = g.layout_auto() # ~7secs in 3.0 GHz 8-core i7
        */
        var cs_lays = {
            "customradial"  : "Gráfico circular",
            "kawai100"      : "Kamada-Kawai * 100",
            "kawai1000"     : "Kamada-Kawai * 1000",
            "kawai2000"     : "Kamada-Kawai * 2000",
            "fr"            : "Fruchterman-Reingold (F-R)",
            "frgrid"        : "F-R en grilla",
            "frcircle"      : "F-R en círculo",
            "circle"        : "Circular",
            "drl"           : "DRL",
            "lgl"           : "LGL",
            "random"        : "Random",
            "graphopt"      : "Graphopt",
            "rt"            : "Reingold-Tilford (R-T)",
            "rtcircle"      : "R-T circular",
            "sugiyama"      : "Sugiyama",
            "mds"           : "MDS",
            "auto"          : "Automático"
        };

        var tmphtml = "<div id=\"cg-setup-form\"><!--select id=\"cg-layout\">\n";
        var k       = "";

        for (k in cs_lays) {
            //console.log(k);
            tmphtml += "<option value=\"" + k + "\" >" + cs_lays[k] + "</option>\n";
        }

        tmphtml += "</select-->\n<button onclick=\"generate_customgraph()\"> Generate Universe </button>";
        tmphtml  = "";


        cg       = tmphtml;
        $("#cg").html( tmphtml );
        setTimeout(generate_customgraph, 100);
    }
}



function show_customgraph(obj) {
    $("#cy, #wc, #gs").fadeOut(100);
    select_graph_UI(obj);

    if (cg === null || cg === undefined) {
        //setup
        app.espere("Loading NewsUniverse, please wait...", "Loaded. Rendering...").then(
            function() {
                generate_customgraph();
            }
        );
    } else {
        $("#cg").fadeIn(500).promise().then(
            function() {
                $("#stats #nodecount").html( universe.nodecount );
                $("#stats h4").html("News (nodes) arranged around the Universe");
                $("#leyenda").html( universe.leyenda_html );
            }
        );
    }

}


function generate_customgraph() {

    var wp_id   = nodeset.nodes[0].data.wp_url.split("p=")[1]
    //var layout  = $("#cg-layout")[0].value
    var layout  = "random";

    $("#cg").css("cursor","wait");

    $.get(
        location.protocol + "//" + location.host + "/get_universe.php?news_id=" + wp_id
    ).promise().then(
        function (resp, status, xhr) {
            //console.log(resp,status,xhr);
            if (resp.status === "success") {
                //setup_customgraph_nodelist( resp.data.svg )
				setup_universe_from_json(resp.data.universe);
                $("#stats #nodecount").html( universe.nodecount );
                $("#stats h4").html("News (nodes) arranged around the Universe");
                $("#leyenda").html( universe.leyenda_html );
            } else {
                var message = resp.data.message;
                alert("error leyendo datos del custom graph:\n" + message);
            }
            $("#cg").css("cursor","default").show(100);
            app.desespere("Loading NewsUniverse, please wait...");
        },

        function(a, b, c) {
            console.log("generate_customgraph fail : ", a,b,c);
            $("#cg").css("cursor","default").show(100);
            app.desespere("Loading NewsUniverse, please wait...");
        }
    );
}

function setup_customgraph_nodelist(svg) {
    var local_cg = $("#cg");
    local_cg.html( svg + cg);
    custom_graph_data = JSON.parse( $("svg > #graph-data").text() );

    var tmparr = [];
    //var tmpcol = "<h4>News Categories</h4>\n";
    var tmpcol = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"100%\" height=\"100%\" viewBox=\"0 0 100 180\" version=\"1.1\">\
    <text x=\"0\" y=\"20\" >News Categories</text>\n";
    var tmpi   = 40;
    for (var k in custom_graph_data) {
        tmparr.push(custom_graph_data[k]);
        var found = false;
        for (var i = 0; i < universe.categories.length; i++) {
            if (custom_graph_data[k]["cats"][0] == universe.categories[i]["name"]) {
                found = true;
                break;
            }
        }

        if (!found) {
            var cat = {
                "name"  :   custom_graph_data[k]["cats"][0],
                "color" :   $("svg g:has(> circle)[objectid=" + custom_graph_data[k]["oid"] + "]").attr("fill")
            };
            universe.categories.push( cat );
            //tmpcol += "<p><div class=\"round\" style=\"background-color:"+cat.color+"\"></div> "+cat.name+"</p>"
            //tmpcol += "<span class=\"round\" style=\"background-color:"+cat.color+"; width:10px; height:10px; position:relative; float:left; display:inline-block; border: 1px black solid;\"></span><small style=\"position:relative;float:left;display:inline-block;\">"+cat.name+"</small><br/>";
            tmpcol += "<circle cx=\"5\" cy=\"" + tmpi  + "\" r=\"5\" fill=\""+cat.color+"\" stroke=\"black\" />\n";
            var textLength = (cat.name.length >= 10 ) ? " textLength=\"85px\" " : "";
            tmpcol += "<text x=\"15\" y=\"" + (tmpi + 5) + "\" font-size=\"15px\" " + textLength + ">"+cat.name+"</text>\n";
            tmpi += 15;
        }

    }

    tmpcol += "</svg>"

    universe.nodecount      = tmparr.length;
    universe.leyenda_html   = tmpcol;

    tmparr.sort(function(a, b) {
        return parseInt(a.id.split("_")[1]) - parseInt(b.id.split("_")[1]);
    });

    var tmphtml = "\n<div id=\"cg-node-list\" class=\"node-list\">\
                    <div class=\"cerrar\" onclick=\"toggle_node_list();\"> X </div>\
                    <div><h2>NewsUniverse Node List.</h2></div>\
                    <div><h3 style=\"color:red;\"> (press \"L\" key to show/hide this list) </h3></div>\
                    <table>\
                        <thead>\
                            <tr>\
                                <th>nodo</th>\
                                <th>fecha</th>\
                                <th>titulo</th>\
                            </tr>\
                        </thead>\
                        <tbody>";
    for (var i = 0; i < tmparr.length; i++) {
        tmphtml += "<tr><td>" + tmparr[i].id.split("_")[1] + "</td><td>" + tmparr[i].date + "</td><td><a class=\"hoverable\" target=\"_blank\" href=\""+tmparr[i].url+"\">" + tmparr[i].title + "</a></td></tr>";
    }
    tmphtml += "</tbody></table></div>";
    local_cg.html( local_cg.html() + tmphtml );

    universe.timer_titulo = null;

    $("g:has(> circle)").off("mouseover").on("mouseover",
        function(evt) {
            if (universe.timer_titulo != null) {
                clearTimeout(universe.timer_titulo);
            }
            var fun   = function() {
                var grupo = $(evt.target.parentNode);
                while (grupo.attr("objectid") == undefined) {
                    grupo = $(grupo[0].parentNode);
                }
                var data  = custom_graph_data[grupo.attr("objectid")];
                mostrar_titulo( data.title + "<br/>Category : " + data.cats[0], data.date );
                grupo.attr("selected", "selected");
                grupo_lineas = $("g.edge-group[objectid="+grupo.attr("objectid")+"]");
                grupo_lineas.attr("selected", "selected");


                //ALEXIS
                grupo_entradas = $("line[target-id="+grupo.attr("objectid")+"]");
                grupo_entradas.each( function( index ){
                    var linea = $(this);
                    linea.attr("selected", linea.attr("selected"));
                    linea.attr("class", "solida")
                    linea.attr("stroke", "red")
                    linea.attr("marker-end", "url(#marker-red-arrow)")
                });
                //>ALEXIS


                if ( $("g[objectid]>circle").length > 50 ) {
                    grupo_lineas.find("line").each( function( index ) {
                        var linea = $(this);
                        linea.attr("stroke-width", linea.attr("alt-stroke-width"));
                        linea.attr("stroke", "blue")
                        linea.attr("marker-end", "url(#marker-blue-arrow)")
                    });
                    //ALEXIS
                    grupo_entradas.each( function( index ){
                        var linea = $(this);
                        linea.attr("stroke-width", linea.attr("alt-stroke-width"));
                    });
                    //>ALEXIS
                }
                universe.timer_titulo = null;
            };

            universe.timer_titulo = setTimeout(fun, 500);
        }
    ).off("mouseout").on("mouseout",
        function (evt) {
            if (universe.timer_titulo != null) {
                clearTimeout(universe.timer_titulo);
                universe.timer_titulo = null;
            }
            ocultar_titulo();
            var grupo = $(evt.target.parentNode);
            while (grupo.attr("objectid") == undefined) {
                grupo = $(grupo[0].parentNode);
            }
            grupo.removeAttr("selected");
            grupo_lineas = $("g.edge-group[objectid="+grupo.attr("objectid")+"]");
            grupo_lineas.removeAttr("selected");

            //ALEXIS
            grupo_entradas = $("line[target-id="+grupo.attr("objectid")+"]");
            grupo_entradas.each( function( index ){
                var linea = $(this);
                linea.removeAttr("selected");
                linea.removeAttr("class")
                linea.attr("stroke", "black")
                linea.attr("marker-end", "url(#marker-arrow)")
            });
            //>ALEXIS

            if ( $("g[objectid]>circle").length > 50 ) {
                grupo_lineas.find("line").each( function( index ) {
                    var linea = $(this);
                    linea.attr("stroke-width", "1");
                    linea.attr("stroke", "black")
                    linea.attr("marker-end", "url(#marker-arrow)")
                });

                //ALEXIS
                grupo_entradas.each( function( index ){
                    var linea = $(this);
                    linea.attr("stroke-width", "1");
                });
                //>ALEXIS
            }
        }
    );
}

function toggle_node_list( ) {
    var divs = $(".node-list");
    divs.each( function(index) {
        div = $(this);
        if ( div.is(":hidden") ) {
            div.fadeIn(500);
        } else {
            div.fadeOut(500);
        }
    });
}

function select_graph_UI(obj) {
    $("#visualizaciones .selected").removeClass("selected");
    $(obj).find("span").addClass("selected");
}


function color_from_category(categories){
        ret = "white";

        if(categories !== undefined){
                category_array = []
                for(var i = 0; i < categories.length; i++){
                        category_array[i] = categories[i].toLowerCase();
                }

                if(category_array.indexOf("policiales") > -1){
                        ret = "rgba(100,100,100,1)";
                }else if(category_array.indexOf("policiales") > -1){
                        ret = "rgba(100,100,100,1)";
                }else if(category_array.indexOf("internacionales") > -1){
                        ret = "rgba(0,200,255,1)";
                }else if(category_array.indexOf("internacionales-pt") > -1){
                        ret = "rgba(0,200,255,1)";
                }else if(category_array.indexOf("economía") > -1){
                        ret = "rgba(255,215,0,1)";
                }else if(category_array.indexOf("economia-pt") > -1){
                        ret = "rgba(255,215,0,1)";
                }else if(category_array.indexOf("interés general") > -1){
                        ret = "rgba(255,255,255,1)";
                }else if(category_array.indexOf("interesse geral-pt") > -1){
                        ret = "rgba(255,255,255,1)";
                }else if(category_array.indexOf("política") > -1){
                        ret = "rgba(255,20,147,1)";
                }else if(category_array.indexOf("política-pt") > -1){
                        ret = "rgba(255,20,147,1)";
                }else if(category_array.indexOf("entretenimiento") > -1){
                        ret = "rgba(0,255,0,1)";
                }else if(category_array.indexOf("entretenimento-pt") > -1){
                        ret = "rgba(0,255,0,1)";
                }else if(category_array.indexOf("salud") > -1){
                        ret = "rgba(255,222,173,1)";
                }else if(category_array.indexOf("saúde-pt") > -1){
                        ret = "rgba(255,222,173,1)";
                }else if(category_array.indexOf("mulher-pt") > -1){
                        ret = "rgba(75,0,130,1)";
                }else if(category_array.indexOf("belleza") > -1){
                        ret = "rgba(255,69,0,1)";
                }else if(category_array.indexOf("mujer") > -1){
                        ret = "rgba(255,69,0,1)";
                }else if(category_array.indexOf("estilo vida") > -1){
                        ret = "rgba(218,112,214,1)";
                }else if(category_array.indexOf("turismo") > -1){
                        ret = "rgba(107,142,35,1)";
                }else if(category_array.indexOf("turismo-pt") > -1){
                        ret = "rgba(107,142,35,1)";
                }else if(category_array.indexOf("cultura-pt") > -1){
                        ret = "rgba(176,224,230,1)";
                }else if(category_array.indexOf("deporte") > -1){
                        ret = "rgba(160,82,45,1)";
                }else if(category_array.indexOf("esporte-pt") > -1){
                        ret = "rgba(160,82,45,1)";
                }else if(category_array.indexOf("clima") > -1){
                        ret = "rgba(220,220,220,1)";
                }else if(category_array.indexOf("clima-pt") > -1){
                        ret = "rgba(220,220,220,1)";
                }else if(category_array.indexOf("ciencia") > -1){
                        ret = "rgba(233,150,122,1)";
                }else if(category_array.indexOf("ciência-pt") > -1){
                        ret = "rgba(233,150,122,1)";
                }else if(category_array.indexOf("tecnología") > -1){
                        ret = "rgba(255,0,0,1)";
                }else if(category_array.indexOf("tecnología-pt") > -1){
                        ret = "rgba(255,0,0,1)";
                }else if(category_array.indexOf("automóviles") > -1){
                        ret = "rgba(189,183,107,1)";
                }else if(category_array.indexOf("electrodomésticos") > -1){
                        ret = "rgba(65,105,225,1)";
                }else if(category_array.indexOf("propiedades") > -1){
                        ret = "rgba(47,79,79,1)";
                }else if(category_array.indexOf("propiedades-pt") > -1){
                        ret = "rgba(47,79,79,1)";
                }
        }
        return ret;
}


function setup_universe_from_json( obj ) {
        var nodes = [];
        var universe_categories = {"starting point": "black"};
        var node_objects = []

        //NODES:
        var node_index = 0;
        while(obj[node_index] !== undefined){
                node_object = obj[node_index];

                if(node_object.title.length > 25){
                        node_object.title = node_object.title.substring(0,22) + "...";
                }
                node_object.id          = node_index.toString();
                node_object.color = color_from_category(node_object.categories);
                if(node_object.level == 0){
                        node_object.color = "black";
                }
                //FILL CATEGORIES
                if(node_object.level != 0 && universe_categories[node_object.categories[0]] === undefined){
                        universe_categories[node_object.categories[0]] = node_object.color;
                }

                //PUSH NODE
                nodes.push({
                                "group": "nodes",
                                "data" : node_object,
                        });

                node_objects.push(node_object);

                node_index++;
        }

        var nodecount = node_index;

        //EDGES:
        var node_index = 0;
        while(obj[node_index] !== undefined){
                node_object = obj[node_index];

                for(var i = 0; i < node_object.edges.length; i++){
                        nodes.push({
                                        "group"            : "edges",
                                        "data"             :{
                                                "id"            : node_index.toString() + "-" + node_object.edges[i][0].toString(),
                                                "source"        : node_index.toString(),
                                                "target"        : node_object.edges[i][0].toString(),
                                        }
                        });
                }
                node_index++;
        }


        //window.nodeset = {
        //        "nodes"         : nodes,
        //        "nodecount" : nodecount
        //};
        //universe.nodecount = nodecount;
        set_universe_data(nodecount, universe_categories, node_objects);
        build_universe(nodes);
        //return {
        //        "nodes" : nodes
        //};
}


function set_universe_data(nodecount, categories, node_objects){
        universe.nodecount = nodecount;

        var colors_svg = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"100%\" height=\"100%\" viewBox=\"0 0 100 180\" version=\"1.1\">"

        colors_svg += "<text x=\"0\" y=\"20\" >News Categories</text>\n";

        var current_heigth = 40;

        for(var category_name in categories){
                var category_color = categories[category_name];

                var text_length_attr = "";
                if(category_name.length >= 10){
                        text_length_attr = " textLength=\"85px\" ";
                }

                colors_svg += "<circle cx=\"5\" cy=\"" + current_heigth + "\" r=\"5\" fill=\"" + category_color + "\" stroke=\"black\" />\n";
                colors_svg += "<text x=\"15\" y=\"" + (current_heigth + 5) + "\" font-size=\"15px\" " + text_length_attr + ">" + category_name + "</text>\n";
                current_heigth += 15;
        }

        colors_svg += "</svg>";

        universe.leyenda_html   = colors_svg;



        node_objects.sort(function(a, b) {
                return parseInt(a.id) - parseInt(b.id);
        });

        var node_list_html = "\n<div id=\"cg-node-list\" class=\"node-list\">\
                        <div class=\"cerrar\" onclick=\"toggle_node_list();\"> X </div>\
                        <div><h2>NewsUniverse Node List</h2></div>\
						<div><h3 style=\"color:black;\">(drag & drop and mouse over nodes for insightful visualizations)</h3></div>\
                        <div><h3 style=\"color:red;\"> (press \"L\" key to show/hide this list) </h3></div>\
                        <table>\
                            <thead>\
                                <tr>\
                                    <th>node</th>\
                                    <th>date</th>\
                                    <th>title</th>\
                                </tr>\
                            </thead>\
                            <tbody>";
        for (var i = 0; i < node_objects.length; i++) {
                node_list_html += "<tr><td>" + node_objects[i].id + "</td><td>" + node_objects[i].date + "</td><td><a class=\"hoverable\" target=\"_blank\" href=\""+node_objects[i].url+"\">" + node_objects[i].title + "</a></td></tr>";
        }
        node_list_html += "</tbody></table></div>";

        var local_cg = $("#cg");
        local_cg.html( local_cg.html() + node_list_html );

        universe.timer_titulo = null;

}


function build_universe(universe_nodes) {
    //Node params:
    var node_size                = 15;
    var font_size                = node_size/3;
    var size_multiplier            = 3;

    //Edge Params:
    var edge_width                = 0.1;
    var edge_opacity            = 0.3;

    //Loading Params:
    var batch_size                = 3000;
    var interval                = 150;



    //console.log(process_json_new( galaxy_json ).nodes);

    var tmp_resize = function() {
        $("#cg")
        .css("width", $(document).width() + "px")
        .css("height",$(document).height() + "px");

        if (window.cg != null) {
            console.log("cg not null");
			console.log(window.cg == '');
            window.setTimeout(10,window.cg.resize);
        } else {
            console.log("cg es null");
        }
    }
    tmp_resize();

    window.cg = cytoscape({
        textureOnViewport: true,
        //pixelRatio: 1,
        wheelSensitivity: 0.1,
        container: document.getElementById('cg'), // container to render in
        elements: [],
        style: [

            {
                selector : 'node',
                style: {
                    'width'                : node_size,
                    'height'            : node_size,
                    'background-color'    : 'data(color)',
                    'border-color'        : 'black',
                    'border-width'        : '1px',
                    'label'                  : 'data(id)',
                    'text-valign'        : 'center',
                    'text-halign'        : 'center',
                    'font-size'            : font_size,
                    'min-zoomed-font-size'    : '5px',
                }
            },

            {
                selector : 'node[level=0]',
                style: {
                    'width'                : node_size*2,
                    'height'            : node_size*2,
                    'shape'                : 'rectangle',
                }
            },

            {
                selector : 'edge',
                style: {
                    "width": edge_width,
                    'line-color' : 'black',
                    'opacity'     : edge_opacity,
                    'target-arrow-shape': 'triangle',
                }
            }
        ],
        layout: {
            name: 'random',
        }

    });

    cg.on("tapdragover","node", function(evt) {
            //console.log("MOUSEOVER");
            var edges = evt.cyTarget.connectedEdges();
            var nodes = edges.connectedNodes();


            var starting = edges.filter("[source=\"" + evt.cyTarget.data().id.toString()+"\"]");
            var ending = edges.filter("[target=\"" + evt.cyTarget.data().id.toString()+"\"]");
            cg.startBatch();
                nodes.css("width"        , node_size*size_multiplier);
                nodes.css("height"       , node_size*size_multiplier);
                nodes.css("font-size"    , font_size*size_multiplier);
                nodes.css("z-index"        , 10000000);

                edges.css("line-style"    , "solid");
                edges.css("opacity"        , "1");
                edges.css("curve-style"    , "bezier");
                edges.css("z-index"        , 10000000);

                starting.css("width"                , 10)
                starting.css("line-color"            , "blue");
                starting.css("target-arrow-color"    , "blue");

                ending.css("width"                , 5)
                ending.css("line-color"            , "red");
                ending.css("target-arrow-color"    , "red");
            cg.endBatch();
    });

    cg.on("tapdragout","node", function(evt) {
        var edges = evt.cyTarget.connectedEdges().filter("[^selected], [selected=0]");
        var nodes = edges.connectedNodes().filter("[^selected], [selected=0]");
        var roots = nodes.filter("[level=0]");


        cg.startBatch();
            nodes.css("width"         , node_size);
            nodes.css("height"       , node_size);
            nodes.css("font-size"    , font_size);
            nodes.css("z-index"        , 0);

            roots.css("width"         , node_size*2);
            roots.css("height"       , node_size*2);

            edges.css("opacity"        , edge_opacity);
            edges.css("width"        , edge_width);
            edges.css("line-color"    , "black");
            edges.css("curve-style"    , "haystack");
            edges.css("z-index"        , 0);
        cg.endBatch();


    });

    cg.on("tap","node", function(evt) {
        //console.log("click");
        var edges = evt.cyTarget.connectedEdges();
        var nodes = edges.connectedNodes();

        already_selected = (evt.cyTarget.data().selected !== undefined && evt.cyTarget.data().selected == 2);


        var selected_nodes = cg.nodes().filter("[selected>=1]");
        var selected_edges = cg.edges().filter("[selected>=1]");


        selected_edges.data("selected", 0);
        selected_nodes.data("selected", 0);

        if(!already_selected){
            nodes.data("selected", 1);
            edges.data("selected", 1);
            evt.cyTarget.data("selected",2);
        }

        nodes = cg.nodes().filter("[^selected], [selected=0]");
        edges = cg.edges().filter("[^selected], [selected=0]");
        var roots = nodes.filter("[level=0]");

        cg.startBatch();
            nodes.css("width"         , node_size);
            nodes.css("height"       , node_size);
            nodes.css("font-size"    , font_size);
            nodes.css("z-index"        , 0);

            roots.css("width"         , node_size*2);
            roots.css("height"       , node_size*2);

            edges.css("opacity"        , edge_opacity)
            edges.css("width"        , edge_width)
            edges.css("line-color"    , "black");
            edges.css("curve-style"    , "haystack");
            edges.css("z-index"        , 0);
        cg.endBatch();

        //console.log(evt.cyTarget.data().selected);
    });


    cg.on("layoutstop", function(evt) {
    });


    //------Incremental Loading-------

    //Disable panning to avoid auto screen repositioning
    cg.panningEnabled( false );

    //Get elements:
    var elements = universe_nodes;
	console.log("---------------");
	console.log(elements);
    function inc_elem(start_from){
        var sub_array = [];


        if(start_from > elements.length){
            //All elements drawn: enable panning and fit view
            cg.panningEnabled( true );
            cg.fit();
			console.log(cg);
			console.log("OK CYTO");
            return;
        }

        if((start_from+batch_size) >= elements.length){
            //Slice remaining elements
            sub_array = elements.slice(start_from, elements.length-1);
        }else{
            //Slice #batch_size elements
            sub_array = elements.slice(start_from, start_from+batch_size);
        }
        //Add new elements and redraw
        cg.add(sub_array).layout({name: 'random'});

        //Process next batch_size after interval
        setTimeout(
                    function(){inc_elem(start_from+batch_size);},
                    interval
                );
        return;
    }

    //Start from 0
    inc_elem(0);
	//console.log("ADD 1");
	//cg.add(elements[0]).layout({name: 'random'});
	//cg.add(elements[1]).layout({name: 'random'});
	//cg.resize();



}
