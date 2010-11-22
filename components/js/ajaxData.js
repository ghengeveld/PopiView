$(document).ready(function(){
	var opts = new Array();
	opts['historic_length'] = $("select[name=historic_length]").val();
	opts['recent_length'] = $("select[name=recent_length]").val();
	opts['qfield'] = $("input[name=qfield]:checked").val();
	opts['tp_timespan'] = $("select[name=tp_timespan]").val();
	opts['kc_timespan'] = $("select[name=kc_timespan]").val();
	opts['external'] = $("input[name=external]").is(":checked")?1:0;
	opts['searches'] = $("input[name=searches]").is(":checked")?1:0;
	opts['internal'] = $("input[name=internal]").is(":checked")?1:0;
	opts['direct'] = $("input[name=direct]").is(":checked")?1:0;

	$("select").change(function(){
		opts[$(this).attr('name')] = $(this).val();
		updateDeviators();
        updateTopPages();
        updateKeywordCloud();
	});
	$("input[type=radio]").change(function(){
		opts[$(this).attr('name')] = $(this).val();
		updateDeviators();
	});

	var monitor_timestamp = 0;
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
	
	function updateDeviators()
	{
		$.getJSON(
			'deviators.json?qfield=' + opts['qfield']
			+ '&historic_length=' + opts['historic_length']
			+ '&recent_length=' + opts['recent_length'],
			function(data)
			{
				var items = '';
				for (x in data){
					items += '<tr>';
					items += '<td>' + data[x].name + '</td>';
					items += '<td class="alignRight">' + data[x].hph_historic + '->' + data[x].hph_recent + ' hits/hour</td>';
					items += '</tr>';
				}
				$('#deviators table').html(items);
			}
		);
	}
	function updateTopPages()
	{
		$.getJSON(
			'toppages.json?timespan=' + opts['tp_timespan'],
			function(data)
			{
				var items = '';
				for (x in data){
					items += '<tr>';
					items += '<td>' + data[x].name + '</td>';
					items += '<td class="alignRight">' + data[x].count + ' hits</td>';
					items += '</tr>';
				}
				$('#toppages table').html(items);
			}
		);
	}
	function updateKeywordCloud()
	{
		$.getJSON('keywordcloud.json?timespan=' + opts['kc_timespan'], function(data){
			var items = '';
			for (x in data){
				items += '<li style="font-size:' + data[x][1] + '%;">' + data[x][0] + '</li>';
			}
			$('#keywordcloud ol').html(items);
		});
	}
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
					item = '<li class="new ' + sourcetype + '" title="'
						+ data[x].url + '"><a href="'
                        + data[x].url + '" target="_blank">'
                        + data[x].title + '</a><br/>'
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
				}, 3000, function(){
					$(this).removeClass('new');
				});
			}
		);
	}

	updateDeviators();
	updateTopPages();
	updateKeywordCloud();
	updateMonitor();
	setInterval(function(){ updateDeviators(); }, 30000);
	setInterval(function(){ updateTopPages(); }, 30000);
	setInterval(function(){ updateKeywordCloud(); }, 30000);
	setInterval(function(){ updateMonitor(); }, 5000);
});
