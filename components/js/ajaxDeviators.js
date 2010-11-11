$(document).ready(function(){
	var opts = new Array();
	opts['historic_length'] = $("select[name=historic_length]").val();
	opts['recent_length'] = $("select[name=recent_length]").val();
	opts['qfield'] = $("input[name=qfield]:checked").val();
	$("select").change(function(){
		opts[$(this).attr('name')] = $(this).val();
		updateDeviators();
	});
	$("input[type=radio]").change(function(){
		opts[$(this).attr('name')] = $(this).val();
		updateDeviators();
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
					items += '<td>' + data[x].hph_historic + '->' + data[x].hph_recent + '</td>';
					items += '</tr>';
				}
				$('#deviators table').html(items);
			}
		);
	}
	updateDeviators();
	setInterval(function(){ updateDeviators(); }, 30000);
});