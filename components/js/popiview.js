function pv()
{
	document.write(
		'<img src="http://popiview.infrae.com/image.gif?cur=' +
			encodeURIComponent(location.href) +
		'&amp;ref=' +
			encodeURIComponent(document.referrer) +
		'&amp;title=' +
			encodeURI(document.title) +
		'" alt="" width="1" height="1" />'
	);
}
