<?php

ob_start("ob_gzhandler");
header('Cache-Control: public');
header('Content-Type:  text/html; charset=UTF-8');

$filename   = "/home/nlt-runner/wordcloud-jsons/" . $_REQUEST["news_id"] . ".json";
$ret        = Array();
$json       = "";
$status     = "success";
$message    = "";

/*if (!isset($_REQUEST["news_id"])) {
    $ret = Array(
        "status"    =>  "error",
        "data"      =>  [],
        "message"   => "News id expected."
    );

    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
    exit();
}*/
if (!isset($_REQUEST["days"]) || !ctype_digit($_REQUEST["days"]) || intval($_REQUEST["days"]) > 5){
	$_REQUEST["days"] = 5;
}


if (!isset($_REQUEST["language"])) {
    $ret = Array(
        "status"    =>  "error",
        "data"      =>  [],
        "message"   => "Language expected."
    );

    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
    exit();
}


try {
  //  if (!file_exists($filename)) {
        $json = shell_exec( "/usr/bin/generate-json-title-cloud " . $_REQUEST["language"] . " " . $_REQUEST["days"] . " 2>&1" );
        $json = json_decode($json);
        foreach($json as $val){
                echo "<a target='_blank' href='http://entretenimientobit.com/?s=".str_replace(" ", "+", trim($val->tag)). "'>";
                echo $val->tag;
                echo "</a>";
                echo ". in ". $val->count . " headlines.";
                echo "<br>";
	}
        exit();
   // }

    /*try {
        $json = file_exists($filename) ? file_get_contents($filename) : "";
    } catch(Exception $e) {
        $message    = "Error reading json: " . $e->getMessage();
        $status     = "error";
    }*/
    
} catch (Exception $e) {
    $status   = "error";
    $message  = "Error reading json: " . $e->getMessage();
}

if (trim($json) == "") {
    //header("Location: http://entretenimientobit.com");
    //exit();
    $status = "fail";
}

$ret = Array(
    "status"    =>  $status,
    "data"      =>  Array( "cloud_data" => json_decode($json), "message" => $message )
);

if ($status === "error") {
    $ret["message"] = $message;
}

if (!isset($_REQUEST["noecho"]) || (isset($_REQUEST["noecho"]) && $_REQUEST["noecho"] === False) ) {
    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
}

?>
