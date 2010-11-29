function pv()
{
	document.write(
		'<img src="${siteconfig:baseurl}/image.gif?cur=' +
			encodeURIComponent(location.href) +
		'&amp;ref=' +
			encodeURIComponent(decodeURI(document.referrer)) +
		'&amp;title=' +
			encodeURIComponent(document.title) +
		'" alt="" width="1" height="1" />'
	);
}
