[app:main]
use = egg:PopiView
storage_name = sql

cfg>>dbtype = ${dbconfig:dbtype}
cfg>>dbhost = ${dbconfig:dbhost}
cfg>>dbuser = ${dbconfig:dbuser}
cfg>>dbpass = ${dbconfig:dbpass}
cfg>>dbname = ${dbconfig:dbname}

cfg>>urlmap>>index = index
cfg>>urlmap>>image.gif = log_hit
cfg>>urlmap>>deviators.json = deviators
cfg>>urlmap>>toppages.json = toppages
cfg>>urlmap>>keywordcloud.json = keywordcloud
cfg>>urlmap>>hitmonitor.json = hitmonitor
cfg>>urlmap>>dummydata = dummydata
cfg>>urlmap>>randomdata = randomdata
cfg>>urlmap>>cleardata = cleardata
cfg>>urlmap>>component = get_component

cfg>>sparams>>google = q
cfg>>sparams>>bing = q
cfg>>sparams>>yahoo = p

cfg>>recenthits_size = ${pvconfig:recenthits_size}
cfg>>title_strip = ${siteconfig:title_strip}
cfg>>whitelist_lvl1 = ${siteconfig:path_whitelist}
cfg>>ip_blacklist = ${siteconfig:ip_blacklist}
cfg>>keyword_ignorelist = ${siteconfig:keyword_ignorelist}

[server:main]
use = egg:PasteScript#wsgiutils
host = ${settings.ini:host}
port = ${settings.ini:port}
