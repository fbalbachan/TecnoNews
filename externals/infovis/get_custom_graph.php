<?php
if (!isset($_REQUEST["news_id"])) {
    header("Location: http://entretenimientobit.com");
    exit();
}

if (!isset($_REQUEST["layout"])) {
    $_REQUEST["layout"] = "customradial";
}

ob_start("ob_gzhandler");
header('Cache-Control: public');
header('Content-Type: application/json; charset=UTF-8');
ini_set('memory_limit', '1000M');

$filename   = "/home/nlt-runner/custom-graphs/" . $_REQUEST["news_id"] . "-" . $_REQUEST["layout"] . ".svg";
$ret        = Array();
$svg        = "";
$status     = "success";
$message    = "";

try {

    if (!file_exists($filename)) {
        $tmp = shell_exec( "/usr/bin/generate-custom-graph " . $_REQUEST["news_id"] . " " .  $_REQUEST["layout"] );
    }

    try {
        $svg = file_exists($filename) ? file_get_contents($filename) : "No svg.";
    } catch(Exception $e) {
        $message    = "Error reading json: " . $e->getMessage();
        $status     = "error";
    }
    
} catch (Exception $e) {
    $status   = "error";
    $message  = "Error reading json: " . $e->getMessage();
}

if (trim($svg) == "") {
    //header("Location: http://entretenimientobit.com");
    //exit();
    $status = "fail";
}

$ret = Array(
    "status"    =>  $status,
    "data"      =>  Array( "svg" => $svg, "message" => $message )
);

if ($status === "error") {
    $ret["message"] = $message;
}

if (!isset($_REQUEST["noecho"]) || (isset($_REQUEST["noecho"]) && $_REQUEST["noecho"] === False) ) {
    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
}

?>
