<?php
if (!isset($_REQUEST["news_id"])) {
    header("Location: http://entretenimientobit.com");
    exit();
}

ob_start("ob_gzhandler");
header('Cache-Control: public');
header('Content-Type: application/json; charset=UTF-8');
ini_set('memory_limit', '1000M');

$filename   = "/home/pi/sentilecto/universe-jsons/" . $_REQUEST["news_id"] . ".json";
$ret        = Array();
$json       = "";
$status     = "success";
$message    = "";

try {
    if (!file_exists($filename)) {
        $tmp = shell_exec( "/home/pi/sentilecto/generate-json-universe " . $_REQUEST["news_id"] );
    }

    try {
        $json = file_exists($filename) ? file_get_contents($filename) : "";
    } catch(Exception $e) {
        $message    = "Error reading json: " . $e->getMessage();
        $status     = "error";
    }
    
} catch (Exception $e) {
    $status   = "error";
    $message  = "Error reading json: " . $e->getMessage();
}

if (trim($json) == "") {
    $status = "fail";
}

$ret = Array(
    "status"    =>  $status,
    "data"      =>  Array( "universe" => json_decode($json,true), "message" => $message )
);

if ($status === "error") {
    $ret["message"] = $message;
}

echo json_encode($ret, JSON_UNESCAPED_UNICODE);

?>
