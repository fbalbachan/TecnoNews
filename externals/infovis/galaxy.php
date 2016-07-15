<!doctype html>
<?php
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
<html>
    <head>
        <meta charset="utf-8">
        <title>News history network<?php echo ($titulo == "") ? "" : " - ".$titulo; ?></title>
        <script type="text/javascript" src="/wp-content/themes/nanomag/js/cytoscape.js-2.6.6/cytoscape.js"></script>
        <script type="text/javascript" src="/wp-includes/js/jquery/jquery.js?ver=1.11.2"></script>
        <script type="text/javascript" src="app.js"></script>
        <script type="text/javascript" src="/wp-content/themes/nanomag/js/jquery.qtip.min.js"></script>
        <script type="text/javascript" src="/wp-content/themes/nanomag/js/cytoscape.js-2.6.6/cytoscape-qtip.js"></script>
        <script defer type="text/javascript" src="/wp-content/themes/nanomag/js/wordcloud2/src/wordcloud2.js"></script>
        <script type="text/javascript" src="infovis.js"></script>

        <link href="/wp-content/themes/nanomag/css/jquery.qtip.min.css" rel="stylesheet" type="text/css" />
        <link href="infovis.css" rel="stylesheet" type="text/css" />
        <link href="app.css" rel="stylesheet" type="text/css" />

        <script type="text/javascript">
            $               = jQuery;
            var wp_id       = <?php echo (isset($_REQUEST["news_id"]) ) ? $_REQUEST["news_id"] : 0; ?> ;
            var topic_arr   = [["Not enough data for topic cloud", 3]];
            var galaxy_json = {};

            $(document).ready(
                function() {

                    $.get(
                        location.protocol + "//" + location.host + "/get_tree.php?news_id=" + wp_id
                    ).promise().then(
                        function (resp, status, xhr) {
                            //console.log(resp,status,xhr);
                            if (resp.status === "success") {
                                galaxy_json = resp.data.tree;
                                setTimeout(setup_cy, 3000);
                            } else {
                                var message = resp.data.message;
                                alert("error leyendo datos de la galaxia:\n" + message);
                            }
                        }
                    );

                }
            );

        </script>
    </head>
    <body>
        <script>
            (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
            (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
            m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
            })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

            ga('create', 'UA-61076814-3', 'auto');
            ga('send', 'pageview');
        </script>
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
            <p style="text-align:center;"><div class="round" style="left:40%;"><img src="selected.png" style="position:absolute; left:0px; top:0px; width:100%; height:100%" class="rounded"/></div></p>
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

        <div id="titulo-noticia"> </div>

        <div id="visualizaciones">
            <h4>Select Infovis Graph</h4>
            <p onclick="show_galaxy(this);"         > <span class="selected" ></span> NewsGalaxy</p>
            <p onclick="show_wordcloud(this);"      > <span class="" ></span> TopicCloud</p>
            <p onclick="show_galaxysummary(this);"  > <span class="" ></span> GalaxySummary</p>
            <p onclick="show_customgraph(this);"    > <span class="" ></span> NewsUniverse</p>
        </div>

        <div id="download">
            <h4>Portable Version</h4>
            <p><a href="/infovis/portable.php?news_id=<?php echo (isset($_REQUEST["news_id"]) ) ? $_REQUEST["news_id"] : 0; ?>" class="download-link" target="downframe"> Click Here </a></p>
            <iframe style="display:none;" id="downframe" name="downframe"></iframe>
            <h4>Download Universe</h4>
            <p><a href="#" onClick="exportCSV();" class="download-link"> Click Here </a><h4>(First select universe option from infovis graph list)</h4></p>
        </div>

        <div id="powered-by">
            <a href="http://natural.do" target="_blank"><img src="naturaltech2.png" /></a>
        </div>
        <div id="wc">&nbsp;</div>
        <div id="gs">&nbsp;</div>
        <div id="cg">&nbsp;</div>
        <div id="cy"></div>
    </body>
</html>
