<?php
	require_once "annotate-web-apps-config.php";
	
	mysql_connect($dbhost, $dbuser, $dbpass);
	mysql_select_db($dbname);
	
	$r = mysql_query("SELECT s.name, t.name FROM section s JOIN status t ON t.id = s.status ORDER BY t.name, s.name");
	
	header("Content-Type: application/xml");
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
?>
<sections>
<?php
	while ($row = mysql_fetch_row($r)) {
		echo " <section id=\"" . htmlspecialchars($row[0]) . "\" status=\"" . htmlspecialchars($row[1]) . "\"/>\n";
	}
?>
</sections>