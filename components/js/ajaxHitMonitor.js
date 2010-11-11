$(document).ready(function(){
	var monitor_timestamp = 0;
	var opts = new Array();
	opts['external'] = $("input[name=external]").is(":checked")?1:0;
	opts['searches'] = $("input[name=searches]").is(":checked")?1:0;
	opts['internal'] = $("input[name=internal]").is(":checked")?1:0;
	opts['direct'] = $("input[name=direct]").is(":checked")?1:0;
	$("input[type=checkbox]").click(function(){
		if ($(this).is(":checked")){
			opts[$(this).attr('name')] = 1;
		} else {
			opts[$(this).attr('name')] = 0;
		}
		$('#hitmonitor ol').html('');
		monitor_timestamp = 0;
		updateMonitor();
	});
	function updateMonitor()
	{
		$.getJSON(
			'hitmonitor.json?last_timestamp=' + monitor_timestamp
			+ '&ext='+opts['external'] + '&sea='+opts['searches']
			+ '&int='+opts['internal'] + '&dir='+opts['direct'],
			function(data)
			{
				var item = '';
				var sourcetype = 'external';
				for (x in data)
				{
					monitor_timestamp = data[x].timestamp;
					if(data[x].source.indexOf('internal') == 0)
					{
						sourcetype = 'internal';
					}
					else if(data[x].source.indexOf('direct') == 0)
					{
						sourcetype = 'direct';
					}
					else if(data[x].source.indexOf('searches') == 0)
					{
						sourcetype = 'searches';
					}
					else
					{
						sourcetype = 'external';
					}
					item = '<li class="new '+sourcetype+'" title="'
						+ data[x].url + '">' + data[x].title + '<br/>'
						+ '<span>' + data[x].source + '</span></li>';
					$('#hitmonitor ol').prepend(item);
					if($('#hitmonitor ol li').length > 20)
					{
						$('#hitmonitor ol li:last').remove();
					}
					if(sourcetype == 'searches')
					{
						updateKeywordCloud();
					}
				}
				$("li.new").animate({
					backgroundColor: "#fff"
				}, 5000, function(){
					$(this).removeClass('new');
				});
			}
		);
	}
	updateMonitor();
	setInterval(function(){ updateMonitor(); }, 5000);
});