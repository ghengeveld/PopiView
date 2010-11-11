$(document).ready(function(){
	function updateKeywordCloud()
	{
		$.getJSON('keywordcloud.json', function(data){
			var items = '';
			for (x in data){
				items += '<li style="font-size:' + data[x][1] + '%;" title="' + data[x][2] + '">' + data[x][0] + '</li>';
			}
			$('#keywordcloud ol').html(items);
		});
	}
	updateKeywordCloud();
	setInterval(function(){ updateKeywordCloud(); }, 30000);
});