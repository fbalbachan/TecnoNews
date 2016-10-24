<?php
    ob_start("ob_gzhandler");
    header('Cache-Control: public');
    // Expire in one day
    header('Expires: ' . gmdate('D, d M Y H:i:s', time() + 86400) . ' GMT');
    header('Content-Type: application/octet-stream');
    header("Content-Transfer-Encoding: Binary");
    header("Content-disposition: attachment; filename=\"NaturalTech Infovis " . $_REQUEST["news_id"] . ".html\"");

    function portable_base64( $path ) {
        $ret    = "";
        $type   = pathinfo($path, PATHINFO_EXTENSION);
        $data   = file_get_contents($path);
        $ret    = 'data:image/' . $type . ';base64,' . base64_encode($data);
        return $ret;
    }

    $ntbase64   = portable_base64("naturaltech2.png");
    $sbase64    = portable_base64("selected.png");

    $ejec = dirname(__FILE__).'/get-news-entry-by-wpid ' . ((int)$_REQUEST["news_id"]);
    if ( !file_exists($ejec) ) {
        $ejec = dirname(__FILE__).'/infovis/get-news-entry-by-wpid ' . ((int)$_REQUEST["news_id"]);
    }
    $json = trim(utf8_decode(shell_exec( $ejec )));
    if (trim($json) == "undefined")
    {
        echo "<b>Error getting news data.</b>";
        exit(1);
    }
    $json = preg_replace("/ObjectId\((.+)\)/Um", "$1", $json);
    $json = preg_replace("/ISODate\((.+)\)/Um", "$1", $json);
    $news_data = json_decode(utf8_encode($json),true);
    $titulo    = $news_data["title"];

?>
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>NaturalTech Infovis<?php echo ($titulo == "") ? "" : " - ".$titulo; ?></title>
        <script type="text/javascript">
            <?php echo file_get_contents("cytoscape.js-2.6.6/cytoscape.min.js") ;?>
        </script>
        <script type="text/javascript">
            <?php echo file_get_contents("jquery.js") ;?>
        </script>
        <script type="text/javascript">
            <?php echo file_get_contents("wordcloud2/src/wordcloud2.min.js");?>
        </script>
        <script type="text/javascript">
            <?php echo file_get_contents("infovis.min.js");?>
        </script>
        <style>
            <?php echo file_get_contents("infovis.min.css");?>
        </style>

        <style>
        @font-face {
            font-family: 'dosisbook';
            src: url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.eot') . "'"; ?>);
            src: url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.eot') . "'"; ?>) format('embedded-opentype'),
                 url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.woff2') . "'"; ?>) format('woff2'),
                 url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.woff') . "'"; ?>) format('woff'),
                 url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.ttf') . "'"; ?>) format('truetype'),
                 url(<?php echo "'" . portable_base64('fonts/dosis-kit/dosis-book-webfont.svg') . "'"; ?>) format('svg');
            font-weight: normal;
            font-style: normal;
        }

        @font-face {
            font-family: 'exoregular';
            src: url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.eot') . "'"; ?>);
            src: url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.eot') . "'"; ?>) format('embedded-opentype'),
                 url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.woff2') . "'"; ?>) format('woff2'),
                 url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.woff') . "'"; ?>) format('woff'),
                 url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.ttf') . "'"; ?>) format('truetype'),
                 url(<?php echo "'" . portable_base64('fonts/exo-kit/exo-regular-webfont.svg') . "'"; ?>) format('svg');
            font-weight: normal;
            font-style: normal;

        }

        #data-overlay > #title-news {
            font-weight     :   bold;
            text-align      :   center;
            font-family     :   exoregular;
            text-shadow     :   0px 0px 15px white;
            font-size       :   280%;
            width           :   100%;
            color           :   white;
        }

        </style>

        <script type="text/javascript">
            $               = jQuery;
            var wp_id       = <?php echo (isset($_REQUEST["news_id"]) ) ? $_REQUEST["news_id"] : 0; ?> ;
            var topic_arr   = [["Not enough data for topic cloud", 3]];
            var galaxy_json = <?php echo file_get_contents("/home/nlt-runner/tree-jsons/" . $_REQUEST["news_id"] . ".json"); ?>;

            $(document).ready(
                function() {
                    setTimeout(setup_cy, 3000);
                }
            );

            function show_wordcloud(obj) {
                $("#cy, #gs, #cg").fadeOut(100);
                $("#visualizaciones div.selected").removeClass("selected");
                $(obj).addClass("selected");
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

                    <?php

                        if (!file_exists("/home/nlt-runner/wordcloud-jsons/" . $_REQUEST["news_id"] . ".json")) {

                            $tmpjson    = json_decode(file_get_contents("/home/nlt-runner/tree-jsons/" . $_REQUEST["news_id"] . ".json") , True);
                            $ids        = [];

                            function tmp_loop_children($nodo) {
                                $ret = [$nodo["id"]];
                                foreach ( $nodo["children"] as $k=>$v ) {
                                    $ret[] = $v["id"];

                                    foreach ( tmp_loop_children($v) as $k2=>$v2 ) {
                                        $ret[] = $v2;
                                    }
                                }
                                return $ret;
                            }

                            //$ids = tmp_loop_children( $tmpjson["root"] );
                            foreach($tmpjson as $nodo){
                                $ids[] = $nodo["id"];
                            }
                            $_REQUEST["related_ids"]    = implode(",",array_unique( $ids ));
                            $_REQUEST["noecho"]         = True;

                            include("get_cloud_data.php");
                        }
                    ?>

                    topic_arr = <?php echo file_get_contents( "/home/nlt-runner/wordcloud-jsons/" . $_REQUEST["news_id"] . ".json" ); ?>;
                    var tmp = function() {
                        setup_wordcloud(topic_arr);
                        $("#wc").css("cursor","default");
                    };
                    setTimeout(tmp,200);
                } else {
                    $("#wc").fadeIn(500);
                }


            }

            function setup_customgraph() {
                if (cy !== null && cy !== undefined) {
                    cg = "";
                    $("#cg").css("cursor","wait");
                    setTimeout(generate_customgraph, 100);
                }
            }

            function generate_customgraph() {
                setup_customgraph_nodelist( $("#cg").html() );
                $("#cg").css("cursor","default");
                $("#stats #nodecount").html( universe.nodecount );
                $("#stats h4").html("News (nodes) arranged around the Universe");
                $("#leyenda").html( universe.leyenda_html );
            }

        </script>
    </head>
    <body>
        <div id="loading-overlay">
            <div>Loading Galaxy. Please wait...</div>
        </div>
        <div id="data-overlay">
            <span id="close-overlay"> X </span>
            <div id="title-news"></div>

            <table>
                <tr id="source">
                    <td class="title"><div class="tag-styled field-name">Source :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="date">
                    <td class="title"><div class="tag-styled field-name">Date :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="summary">
                    <td class="title"><div class="tag-styled field-name">Summary :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="url">
                    <td class="title"><div class="tag-styled field-name">URL:</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="sentiment">
                    <td class="title"><div class="tag-styled field-name">Sentiment Analysis :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="countries">
                    <td class="title"><div class="tag-styled field-name">Countries :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="categories">
                    <td class="title"><div class="tag-styled field-name">Categories :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

                <tr id="tags">
                    <td class="title"><div class="tag-styled field-name">Tags :</div></td>
                    <td class="value"><div class="tag-styled">&nbsp;</div></td>
                </tr>

            </table>

        </div>
        <div id="leyenda">
            <h4>Sentiment Analysis</h4>
            <p><div class="rojo round" ></div> negative</p>
            <p><div class="verde round"></div> positive</p>
            <p><div class="blanco round"></div> neutral</p>

            <h4>Starting point:</h4>
            <p style="text-align:center;"><div class="round" style="left:40%;"><img src="<?php echo($sbase64); ?>" style="position:absolute; left:0px; top:0px; width:100%; height:100%" class="rounded"/></div></p>
        </div>

        <div id="stats">
            <h4>News (nodes) arranged around the galaxy</h4>
            <p id="nodecount">0</p>
        </div>

        <div id="page-title">
            <div class="cerrar" onclick="$('#page-title').remove();"> X </div>
            <h1>News Galaxy</h1>
            <?php echo ($titulo == "") ? "" : "<h3>".$titulo."</h3>\n"; ?>
            <h4>(drag and drop nodes for insightful visualizations)</h4>
            <h4>(mouse over and click on nodes for details and news summary)</h4>
        </div>

    <div id="titulo-noticia">

        </div>

        <div id="visualizaciones">
            <h4>Select Infovis Graph</h4>
            <p onclick="show_galaxy(this);"         > <span class="selected" ></span> NewsGalaxy</p>
            <p onclick="show_wordcloud(this);"      > <span class="" ></span> TopicCloud</p>
            <p onclick="show_galaxysummary(this);"  > <span class="" ></span> GalaxySummary</p>
            <p onclick="show_customgraph(this);"    > <span class="" ></span> NewsUniverse</p>
        </div>

        <div id="powered-by">
            <a href="http://natural.do" target="_blank"><img src="<?php echo($ntbase64); ?>" /></a>
        </div>
        <div id="wc">&nbsp;</div>
        <div id="gs">&nbsp;</div>
        <div id="cg">
            <?php
                $_REQUEST["layout"] = "random";
                $_REQUEST["noecho"] = True;
                if (!file_exists("/home/nlt-runner/custom-graphs/" . $_REQUEST["news_id"] . "-" . $_REQUEST["layout"] . ".svg")) {
                    include( "get_custom_graph.php" );
                }
                echo file_get_contents("/home/nlt-runner/custom-graphs/" . $_REQUEST["news_id"] . "-" . $_REQUEST["layout"] . ".svg"); ?>
        </div>
        <div id="cy"></div>
    </body>
</html>
