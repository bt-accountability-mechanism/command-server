<?php

header("Access-Control-Allow-Origin: *");

$refs = array(
    'left' => 'LEFT',
    'right' => 'RIGHT',
    'straight_on' => 'GO',
    'turn_around' => 'TURN',
    'toot' => 'TOOT',
    'reset' => 'RESET',
    'passive_mode' => 'PASSIVE_MODE',
    'active_mode' => 'FULL_MODE',
    'dock_mode' => 'DOCKING_MODE',
    'safe_mode' => 'SAFE_MODE',
    'cleaning_mode' => 'CLEANING_MODE'
);
if (isset($_GET['action']) && isset($refs[$_GET['action']])) {
	$action = $refs[$_GET['action']]; 
} else if (isset($_POST['message'])) {
	$action = 'LOG';
} else {
	$action = null;
}

$path = '/home/ubuntu/command-server/';
$file = 'middleware.py';
if ($action === 'LOG') {
	chdir($path);
	echo shell_exec('./'.$file.' '.$action.' '.escapeshellarg($_POST['message']));
} else if ($action !== null) {
	chdir($path);
	$finished = (isset($_GET['finished']) && strtolower($_GET['finished']) == 'true' ? 'true' : 'false');

	echo shell_exec('./'.$file.' '.$action.' '.$finished);
} else {
	http_response_code(400);
	echo 'Invalid request, please notice our following api format: http://URL.de?action=(toot|straight_on|left|right|turn_around|reset|dock_mode|passive_mode|active_mode|safe_mode|cleaning_mode)';
}
