<?php
/*
 * Encoding Functions by Lachlan Hunt
 * http://lachy.id.au/dev/tools/unicode/
 */

function isUTF8($str) {
	return preg_match('/^([\x09\x0A\x0D\x20-\x7E]|[\xC2][\xA0-\xBF]|[\xC3-\xDF][\x80-\xBF]|\xE0[\xA0-\xBF][\x80-\xBF]|[\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}|\xED[\x80-\x9F][\x80-\xBF]|\xF0[\x90-\xBF][\x80-\xBF]{2}|[\xF1-\xF3][\x80-\xBF]{3}|\xF4[\x80-\x8F][\x80-\xBF]{2})*$/', $str);
}

function isASCII($str) {
	return preg_match('/^([\x09\x0A\x0D\x20-\x7E])*$/', $str);
}

function isISO88591($str) {
	return preg_match('/^([\x09\x0A\x0D\x20-\x7E\xA0-\xFF])*$/', $str);
}

function isCP1252($str) {
	return preg_match('/^([\x09\x0A\x0D\x20-\x7E\x80\x82-\x8C\x8E\x91-\x9C\x9E-\xFF])*$/', $str);
}

if (!function_exists('mb_strlen')) {
	function mb_strlen($str) {
		return strlen(utf8_decode($str));
	}
}
?>