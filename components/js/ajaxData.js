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

    // Updates are triggered round-robin
    // Some browsers don't allow more than 2 concurrent connections
    // The hitMonitor is updated every loop, the other monitors once every multiplier loops
    var loopDelay       = 5000;
    var hitMultiplier   = 3;
    var loopCounter     = hitMultiplier;
    var loopTimeout;
    
	$("select").change(function(){
		opts[$(this).attr('name')] = $(this).val();
        instantReset();
	});
	$("input[type=radio]").change(function(){
		opts[$(this).attr('name')] = $(this).val();
        instantReset();
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
        instantReset();
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
					items += '<td class="maxWidth">' + data[x].name + '</td>';
					items += '<td class="alignRight noWrap">' + data[x].hph_historic + '->' + data[x].hph_recent + ' hits/hour</td>';
					items += '</tr>';
				}
				$('#deviators table').html(items);
                updateTopPages();
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
					items += '<td class="maxWidth">' + data[x].name + '</td>';
					items += '<td class="alignRight noWrap">' + data[x].count + ' hits</td>';
					items += '</tr>';
	 			}
				$('#toppages table').html(items);
                updateKeywordCloud();
	 		}
		);
	} 
	function updateKeywordCloud()
	{
		$.getJSON('keywordcloud.json?timespan=' + opts['kc_timespan'], 
            function(data){
			    var items = '';
    			for (x in data){
	    			items += '<li style="font-size:' + data[x][1] + '%;">' + data[x][0] + '</li>';
		    	}
			    $('#keywordcloud ol').html(items);
	            updateMonitor();
		    }
        );
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
                    monitor_timestamp = Math.max(monitor_timestamp, data[x].timestamp);
                    if (data[x].source) {
                        if (data[x].source.indexOf('internal') == 0)
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
				}

				$("li.new").animate({
					backgroundColor: "#fff"
				}, 3000, function(){
					$(this).removeClass('new');
				});

                clearTimeout(loopTimeout);
                if (loopCounter >= hitMultiplier) {
                    loopCounter = 1;
                    loopTimeout = setTimeout(updateDeviators, loopDelay);
                } else {
                    loopCounter += 1;
                    loopTimeout = setTimeout(updateMonitor, loopDelay);
                } 
			}
		);
	}

    // Timeout error for ajax-requests 
    $.ajaxSetup({"error":function(XMLHttpRequest,textStatus, errorThrown) {
        clearTimeout(loopTimeout);
        loopCounter = hitMultiplier;
        loopTimeout = setTimeout(updateDeviators, loopDelay);
    }});

    function instantReset() {
        clearTimeout(loopTimeout);
        loopCounter = hitMultiplier;
        updateDeviators();
    }

    // Start it all up
    updateDeviators();
});
