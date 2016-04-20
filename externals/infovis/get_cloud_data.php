<?php

header('Content-Type: application/json; charset=UTF-8');

$filename   = "/home/nlt-runner/wordcloud-jsons/" . $_REQUEST["news_id"] . ".json";
$ret        = Array();
$json       = "";
$status     = "success";
$message    = "";

if (!isset($_REQUEST["news_id"])) {
    $ret = Array(
        "status"    =>  "error",
        "data"      =>  []
        "message"   => "News id expected."
    );

    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
    exit();
}

if (!isset($_REQUEST["related_ids"])) {
    $ret = Array(
        "status"    =>  "error",
        "data"      =>  []
        "message"   => "Related news ids expected."
    );

    echo json_encode($ret, JSON_UNESCAPED_UNICODE);
    exit();
}


try {

    if (!file_exists($filename)) {
        $tmp = shell_exec( "/usr/bin/generate-json-topic-cloud " . $_REQUEST["news_id"] . " " . $_REQUEST["related_ids"] );
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
    //header("Location: http://entretenimientobit.com");
    //exit();
    $status = "fail";
}

$ret = Array(
    "status"    =>  $status,
    "data"      =>  Array( "cloud_data" => $json, "message" => $message )
);

if ($status === "error") {
    $ret["message"] = $message;
}

echo json_encode($ret, JSON_UNESCAPED_UNICODE);

?>
