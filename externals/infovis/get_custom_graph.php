<?php
if (!isset($_REQUEST["news_id"])) {
    header("Location: http://entretenimientobit.com");
    exit();
}

if (!isset($_REQUEST["layout"])) {
    $_REQUEST["layout"] = "random";
}

if (!isset($_REQUEST["w"])) {
    $_REQUEST["w"] = "1280";
}

if (!isset($_REQUEST["h"])) {
    $_REQUEST["h"] = "1024";
}

ob_start("ob_gzhandler");
header('Cache-Control: public');
header('Content-Type: application/json; charset=UTF-8');
ini_set('memory_limit', '1000M');

$filename   = "/home/nlt-runner/custom-graphs/" . $_REQUEST["news_id"] . "-" . $_REQUEST["layout"] . "-" . $_REQUEST["w"] . "-" . $_REQUEST["h"] . ".svg";
$ret        = Array();
$svg        = "";
$status     = "success";
$message    = "";

try {

    if (!file_exists($filename)) {
        $tmp = shell_exec( "/usr/bin/generate-custom-graph " . (int)$_REQUEST["news_id"] . " " .  str_replace("|","",str_replace("&","", $_REQUEST["layout"])) . " " . (int)$_REQUEST["w"] . " " . (int)$_REQUEST["h"]);
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

if (trim($svg) == "" || trim($svg) == "No svg.") {
    //header("Location: http://entretenimientobit.com");
    //exit();
    $status     = "fail";
    $message    = "Couldn't generate graphic.";
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
