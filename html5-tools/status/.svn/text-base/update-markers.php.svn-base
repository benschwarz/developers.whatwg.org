<?php
header("Content-Type: text/html; charset=UTF-8");
require_once "Email.php";
require_once "encoding-functions.php";
require_once "annotate-web-apps-config.php";

/*
 * IMPORTANT: when testing for yourself, change the email address to your own
 *            in the call to $mail->addRecipient(...)
 *
 * TODO:
 *
 * Twitter message: "Status Update: $rationale"
 * 
 * Finish writing the code to send appropriate emails
 * - May want to log more information about the user in the request email
 *   e.g. IP Address, User Agent.
 * - Confirmation requests probably to Hixie
 * - Confirmed status updates to commit-watches
 * Write the confirmation system to check in updates to the DB
 * - Add a better UI to allow user to confirm individual changes
 */
?>
<!DOCTYPE html>
<?php
$email = '';
$rationale = '';
$status = array();

// Get the values from the REQUEST parameters
foreach ($_REQUEST as $name => $value) {
	if ($name == 'email') {
		$email = $value; // XXX do stripslashes() here and below?
	} elseif ($name == 'rationale') {
		$rationale = $value;
	} elseif ($value == 'TBW' || $value == 'WIP' || $value == 'SCS' || $value == 'none') {
		// Ignore any other values, including empty values.
		$status[addslashes($name)] = $value;
	}
}

// Ensure that email and rationale were provided
if ($email == '' || !Email::isValidEmail($email)
 || $rationale == '' || !isUTF8($rationale) || mb_strlen($rationale) > 125) {
	getMissingInfo($email, $rationale, $status);
} else if ($_SERVER['PATH_INFO'] == '/confirm') {
	updateDB($email, $rationale, $status);
	outputConfirmed();
} else {
	$body = getMailConfirmRequest($email, $rationale, $status);
	$sig = "HTML5 Status Updates\nhttp://www.whatwg.org/html5";

	$mail = new Email();
	$mail->setSubject("HTML5 Status Update");
	$mail->addRecipient('To', 'whatwg@lachy.id.au', 'Lachlan Hunt');
	$mail->setFrom("whatwg@whatwg.org", "WHATWG");
	$mail->setSignature($sig);
	$mail->setText($body);
	$mail->send();

	outputConfirmation($body, $sig);
}

function getMissingInfo($email, $rationale, $status) {
?>
	<title>Update Status Error</title>
    <p>You must provide a valid email address and rationale that is &le; 125 characters.</p>
	<form method="post" action="">
		<p><label for="email">Email: <input type="email" name="email" id="email" value="<?php echo htmlspecialchars($email); ?>"></label>
		<p><label for="rationale">Rationale: <input type="text" name="rationale" id="rationale" maxlength="125" size="70" value="<?php echo htmlspecialchars($rationale); ?>"></label>
		<p><input type="submit" value="save">
<?php
	foreach ($status as $name => $value) {
		echo "		<input type=\"hidden\" name=\"" . htmlspecialchars($name) . "\" value=\"" . htmlspecialchars($value) . "\">\n";
	}
?>        
    </form>
<?php
}

function getMailConfirmRequest($email, $rationale, $status) {
	$body  = "The following changes were requested by $email\n";
	$body .= "Rationale: $rationale\n\n";
//	$url = 'http://status.whatwg.org/update-markers.php?email=' . urlencode($email)
	$url = 'http://html5.lachy.id.au/status/update-markers/confirm?email=' . urlencode($email)
	     . '&rationale=' . urlencode($rationale);

	foreach ($status as $name => $value) {
		$body .= "$name: $value\n";
		$url  .= '&'.urlencode($name).'='.urlencode($value);
	}
	
	$body .= "\nConfirm these changes:\n$url\n";
	return $body;
}

function outputConfirmation($body, $sig) {
?>
	<title>Update Status Confirmation</title>
	<p>Your changes need to be confirmed before they will be committed.
	   The following request has been sent:
	<pre><?php echo "$body\n-- \n$sig"?></pre>
<?php
}

function outputConfirmed() {
?>
	<title>Status Update Confirmed</title>
	<p>The changes have been confirmed,
<?php
}

function updateDB($email, $rationale, $status) {
	global $dbhost, $dbuser, $dbpass, $dbname;
	mysql_connect($dbhost, $dbuser, $dbpass);
	mysql_select_db($dbname);

	$query = 'SELECT * FROM status;';
	$statusTable = mysql_query($query);
	$statusId = array();
	while ($row = mysql_fetch_row($statusTable)) {
		$statusId[$row[1]] = $row[0];
	}

	foreach ($status as $name => $value) {
		if ($value == 'none') {
			$query = "DELETE FROM `section` WHERE name = '$name';";
		} else {
			$query = "UPDATE section SET status = $statusId[$value] WHERE name = '$name'";
			mysql_query($query);
			if (mysql_affected_rows() == 0) {
				$query = "INSERT INTO section (`id`,`name`,`status`) VALUES (NULL , '$name', '$statusId[$value]');";
				mysql_query($query);
			}
		}
		//echo "$query | " . mysql_affected_rows() . "\n";
	}
}
?>
