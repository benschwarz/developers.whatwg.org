<?php
/**
 * Class to create and send emails.
 *
 * PHP version 5
 *
 * @author     Lachlan Hunt <lachlan.hunt@lachy.id.au>
 * @author     Simon Pieters <zcorpan@gmail.com>
 * @copyright  2007 WHATWG
 * @license    http://www.apache.org/licenses/LICENSE-2.0  Apache License 2.0
 */

require_once 'encoding-functions.php';

/*
 * Email class for creating and sending emails.
 *
 * This Email class can be used to create and send emails. All emails are
 * plain text, encoded in UTF-8 and comply with the RFC 3676 (format=flowed).
 * The API allows for multiple recipients to be added and makes it easy to
 * set the subject, main body and signature.
 */
class Email {
	private $headers = array();
	private $to      = array();
	private $cc      = array();
	private $bcc     = array();
	private $from    = '';

	private $subject = '';
	private $body    = '';
	private $sig     = '';

	function __construct() {
		$this->headers['MIME-Version'] = 'MIME-Version: 1.0';
		$this->headers['Content-Type'] = 'Content-Type: text/plain; charset=UTF-8; format=flowed';
	}

	function __destruct() {
	}

	// Private Functions
	/**
	 * Format a name and email address to fit the RFC 2822 addr-spec token.
	 *
	 * If only an email address is supplied, it retuns it as is.
	 * e.g. user@example.com
	 * If a name is also supplied, the name is included as a quoted string
	 * followed by the email address in angle brackets.  Double quotes (") and
	 * backslashes (\) are escaped if any occur within the name.
	 * e.g. "Jack O'Neill" <jack.oneill@example.com>
	 *
	 * @param string $email The email address must comply with the RFC 2822
	 *                      addr-spec token.
	 * @param string $name  The name of the person to whom the email address
	 *                      belongs.
	 * @return string the formatted name and email address.
	 * @access private
	 */
	private function address($email, $name = '') {
		$fieldValue = '';
		if (self::isValidEmail($email)) {
			if ($name != '') {
				$fieldValue  = isASCII($name) ? '"'.addcslashes($name, '"\\').'"' : '=?UTF-8?B?' . base64_encode($name) . '?=';
				$fieldValue .= " <$email>";
			} else {
				$fieldValue = $email;
			}
		}
		return $fieldValue;
	}

	/**
	 * Word wrap lines at the specified length.
	 *
	 * Lines are broken at or before the specified width and the specified
	 * string is intserted at the break.  Existing line breaks are taken into
	 * account. If $cut is set to false, lines are only broken at whitespace.
	 * Lines longer than the specified width may occur if there is no whitespace
	 * prior to that point. If $cut is set to true, then lines are always broken
	 * at the specified length.
	 *
	 * @param string $str   The input string.
	 * @param int    $width The column width. Defaults to 75.
	 * @param string $break The line is broken using the optional break parameter.
	 *               Defaults to '\n'.
	 * @param bool   If the cut is set to TRUE, the string is always wrapped at
	 *               the specified width. So if you have a word that is larger
	 *               than the given width, it is broken apart.
	 * @return string the given string wrapped at the specified column.
	 * @access private
	 */
	private function preserve_wordwrap($str, $width = 75, $break = "\n", $cut = false) {
		// Note: this does not correctly deal with wrapping quoted lines beginning with: >
		$linewrap = create_function('$l', 'return wordwrap($l, ' . $width . ', ' . var_export($break, true) . ', ' . var_export($cut, true) . ');');

		$lines = explode("\n", $str);
		$lines = array_map($linewrap, $lines);
		return implode("\n", $lines);
	}


	// Public Functions
	/**
	 * Add a recipient's name and email address in the To, CC or BCC fields.
	 *
	 * @param string $type  Either 'To', 'CC' or 'BCC' (case insensitive).
	 * @param string $email The email address of the recipient.
	 * @param string $name  The name of the recipient.
	 * @returns void
	 * @access public
	 */
	public function addRecipient($type, $email, $name = '') {
		$fieldValue = $this->address($email, $name);

		if ($fieldValue != '') {
			switch (strtolower($type)) {
			case 'to':
				array_push($this->to, $fieldValue);
				break;
			case 'cc':
				array_push($this->cc, $fieldValue);
				break;
			case 'bcc':
				array_push($this->bcc, $fieldValue);
				break;
			}
		}
	}

	/**
	 * Specify the name and email address of the sender.
	 *
	 * @param string $email The email address of the sender.
	 * @param string $name  The name of the sender.
	 * @returns void
	 * @access public
	 */
	public function setFrom($email, $name = '') {
		$this->from = $this->address($email, $name);
	}

	/**
	 * Specify the subject of the email.
	 *
	 * Set the Subject header field of the email.  If the specified text
	 * contains line breaks, they will be replaced with a single space.
	 * If it contains non-US-ASCII characters, the string will be Base64
	 * encoded as UTF-8.
	 *
	 * @param $text The subject of the email.
	 * @ returns void
	 * @access public
	 */
	public function setSubject($text) {
		$this->subject = preg_replace("/(\r\n|\r|\n)/", " ", $text); // Strip line breaks
		$this->subject = isASCII($this->subject) ? $text : '=?UTF-8?B?' . base64_encode($this->subject) . '?=';
	}

	public function setSignature($text) {
		// strip trailing spaces and normalize linebreaks
		$this->sig = preg_replace("/ *(\r\n|\r|\n)/", "\n", $text);
	}

	public function setText($text) {
		// strip trailing spaces and normalize linebreaks
		$this->body = preg_replace("/ *(\r\n|\r|\n)/", "\n", $text);
	}

	public function send() {
		$headerFields = implode("\r\n", $this->headers);

		if (count($this->to) > 0) {
			$toField = implode(", \r\n\t", $this->to);
		}

		if (count($this->cc) > 0) {
			$headerFields .= "\r\nCc: " . implode(", \r\n\t", $this->cc);
		}

		if (count($this->bcc) > 0) {
			$headerFields .= "\r\nBcc: " . implode(", \r\n\t", $this->bcc);
		}

		if ($this->from != '') {
			$headerFields .= "\r\nFrom: $this->from";
		}

		$message = $this->preserve_wordwrap("$this->body\n-- \n$this->sig", 72, " \n", false);
		$message = $this->preserve_wordwrap($message, 990, "\n", true);
		$message = preg_replace("/(^|\r\n|\n)(>| |From )/", "$1 $2", $message); // space-stuffing

		// Use this for debugging
		// echo "To: $toField\nSubject: $this->subject\n$headerFields\n\n$message";

		mail($toField, $this->subject, $message, $headerFields);
	}

	public static function isValidEmail($email) {
		$pattern = "/^[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/i";
		return preg_match($pattern, $email);
	}
}

// Old function, to be removed later
// Send a mail as UTF-8.
/*
function sendMail($toName, $toEmail, $body) {
	if (isValidEmail($toEmail)) {
		$to       = "=?UTF-8?B?" . base64_encode($toName) . "?= <$toEmail>";
		$subject  = "=?UTF-8?B?" . base64_encode("HTML5 Status Update") . "?=";
		$sig      = "HTML5 Status Updates\r\nhttp://www.w3.org/html/\r\nhttp://www.whatwg.org/";
		$body     = preg_replace("/ *(\r\n|\r|\n)/", "\r\n", $body); // strip trailing spaces and normalize linebreaks
		// XXX change wordwrap to utf8_wordwrap on the next 2 lines
		$body     = wordwrap($body, 72, ' \r\n', false); // soft linebreaks, but preserve words longer than 72 characters
		$body     = wordwrap($body, 990, '\r\n', true);
		$body     = preg_replace("/(^|\r\n)(>| |From )/", "$1 $2", $body); // space-stuffing
		$message  = "$body\r\n-- \r\n$sig";
		$headers  = "MIME-Version: 1.0\r\n";
		$headers .= "Content-Type: text/plain; charset=utf-8; format=flowed\r\n";
		$headers .= "From: =?UTF-8?B?" . base64_encode("HTML5 Status") . "?= <whatwg@whatwg.org>";

		mail($to, $subject, $message, $headers);
	}
}
*/
?>
