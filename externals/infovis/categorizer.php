<meta http-equiv="content-type" content="text/html; charset=utf-8"></meta>
<?php
	$params = "";
	if (!isset($_REQUEST["days"]) || !ctype_digit($_REQUEST["days"]) || intval($_REQUEST["days"]) > 30 || intval($_REQUEST["days"]) < 1){
		$_REQUEST["days"] = 1;
	}
	if (!isset($_REQUEST["language"]) || !ctype_digit($_REQUEST["language"]) || intval($_REQUEST["language"]) > 2 || intval($_REQUEST["language"]) < 1){
		$_REQUEST["language"] = "spanish";
	}else{
		if ($_REQUEST["language"] == 1){
			$_REQUEST["language"] = "spanish";
		}else{
			$_REQUEST["language"] = "portuguese";
		}
	}

	$params = $params." ".$_REQUEST["days"]." ".$_REQUEST["language"];

	if (!isset($_REQUEST["categories"]) || !is_array($_REQUEST["categories"])){
		$_REQUEST["categories"] = [0];
	}

	$params = $params." ".count($_REQUEST["categories"]);

	foreach ($_REQUEST["categories"] as $a => $b) {
		if  (!ctype_digit($b) || intval($b) > 16 || intval($b) < 0) {
			$_REQUEST["categories"][$a] = 0;
		}

		$curr = intval($_REQUEST["categories"][$a]);
		//echo $_REQUEST["categories"][$a];
		if ($_REQUEST["language"] == "spanish"){
			if ($curr == 0){ $_REQUEST["categories"][$a] = "all"; }
			elseif ($curr == 1) { $_REQUEST["categories"][$a] = "internacionales"; }
			elseif ($curr == 2) { $_REQUEST["categories"][$a] = "política"; }
			elseif ($curr == 3) { $_REQUEST["categories"][$a] = "economía"; }
                        elseif ($curr == 4) { $_REQUEST["categories"][$a] = "tecnología"; }
                        elseif ($curr == 5) { $_REQUEST["categories"][$a] = "turismo"; }
                        elseif ($curr == 6) { $_REQUEST["categories"][$a] = "deporte"; }
                        elseif ($curr == 7) { $_REQUEST["categories"][$a] = "entretenimiento"; }
                        elseif ($curr == 8) { $_REQUEST["categories"][$a] = "mujer"; }
                        elseif ($curr == 9) { $_REQUEST["categories"][$a] = "estilo_vida"; }
                        elseif ($curr == 10) { $_REQUEST["categories"][$a] = "automóviles"; }
                        elseif ($curr == 11) { $_REQUEST["categories"][$a] = "ciencia"; }
                        elseif ($curr == 12) { $_REQUEST["categories"][$a] = "policiales"; }
                        elseif ($curr == 13) { $_REQUEST["categories"][$a] = "propiedades"; }
                        elseif ($curr == 14) { $_REQUEST["categories"][$a] = "salud"; }
                        elseif ($curr == 15) { $_REQUEST["categories"][$a] = "electrodomésticos"; }
			elseif ($curr == 16) { $_REQUEST["categories"][$a] = "interés_general"; }
			else {$_REQUEST["categories"][$a] = "NONE";}
		} else {
                        if ($curr == 0){ $_REQUEST["categories"][$a] = "all"; }
                        elseif ($curr == 1) { $_REQUEST["categories"][$a] = "internacionales-pt"; }
                        elseif ($curr == 2) { $_REQUEST["categories"][$a] = "política-pt"; }
                        elseif ($curr == 3) { $_REQUEST["categories"][$a] = "economia-pt"; }
                        elseif ($curr == 4) { $_REQUEST["categories"][$a] = "tecnología-pt"; }
                        elseif ($curr == 5) { $_REQUEST["categories"][$a] = "turismo-pt"; }
                        elseif ($curr == 6) { $_REQUEST["categories"][$a] = "esporte-pt"; }
                        elseif ($curr == 7) { $_REQUEST["categories"][$a] = "entretenimento-pt"; }
                        elseif ($curr == 8) { $_REQUEST["categories"][$a] = "mulher-pt"; }
                        elseif ($curr == 11) { $_REQUEST["categories"][$a] = "ciência-pt"; }
                        elseif ($curr == 12) { $_REQUEST["categories"][$a] = "policiais-pt"; }
                        elseif ($curr == 13) { $_REQUEST["categories"][$a] = "propiedades-pt"; }
                        elseif ($curr == 14) { $_REQUEST["categories"][$a] = "saúde-pt"; }
                        elseif ($curr == 16) { $_REQUEST["categories"][$a] = "interesse_geral-pt"; }
                        else {$_REQUEST["categories"][$a] = "NONE";}

		}
		$params = $params." ".$_REQUEST["categories"][$a];
	}
	
	//echo "AAA";
	//echo "<br>";
	//echo $_REQUEST["language"];
	//echo "<br>";
	//echo $_REQUEST["days"];
	//echo "<br>";
	//echo $_REQUEST["categories"][0];
	//echo "<br>";
	//echo $params;
	//echo "<br>";

	try {
        	$json = shell_exec( "/usr/bin/generate-json-categories" . $params . " 2>&1" );
		//echo $json;
                //exit();
	        $json = json_decode($json);
                foreach($json->stats as $val){
			echo "<center>".$val."</center><br>";
		}
		echo "<br><br><hr>";
		echo "<table align='center' border='1'><tr>    <th>Categories</th>    <th>Type</th>  <th>Title</th> <th>Time Stamp</th> </tr>";
        	foreach($json->entries as $val){
			echo "<tr>";
			echo "<td>".implode(", ", $val->categories)."</td><td>".$val->type."</td><td>";
			if (empty($val->wp_url)){
				echo "<a target='_blank' href='".$val->url."'>".$val->title."</a>";
			}else{
				echo "<a target='_blank' href='".$val->wp_url."'>".$val->title."</a>";
			}
			echo "</td><td>".$val->generation_time;

			echo "</td></tr>";
                }
		echo "</table>";
                //	echo "<a target='_blank' href='http://entretenimientobit.com/?s=".str_replace(" ", "+", trim($val->tag)). "'>";
	        //        echo $val->tag;
        	//        echo "</a>";
                //	echo ". in ". $val->count . " headlines.";
	        //        echo "<br>";
		//}
        	exit();
    
	} catch (Exception $e) {
	    $status   = "error";
	    $message  = "Error reading json: " . $e->getMessage();
	}
?>

