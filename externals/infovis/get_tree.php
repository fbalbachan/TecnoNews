<?php
if (!isset($_REQUEST["news_id"])) {
    header("Location: http://entretenimientobit.com");
    exit();
}

ob_start("ob_gzhandler");
header('Cache-Control: public');
header('Content-Type: application/json; charset=UTF-8');
ini_set('memory_limit', '1000M');

$filename   = "/home/nlt-runner/tree-jsons/" . $_REQUEST["news_id"] . ".json";
$ret        = Array();
$json       = "";
$status     = "success";
$message    = "";

try {

    if (!file_exists($filename)) {
        $tmp = shell_exec( "/usr/bin/generate-json-news-tree " . $_REQUEST["news_id"] );
    }

    try {
        $json = file_exists($filename) ? file_get_contents($filename) : "No json.";
    } catch(Exception $e) {
        $message    = "Error reading json: " . $e->getMessage();
        $status     = "error";
    }
    
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
    "data"      =>  Array( "tree" => json_decode($json,true), "message" => $message )
);

if ($status === "error") {
    $ret["message"] = $message;
}

echo json_encode($ret, JSON_UNESCAPED_UNICODE);

?>
