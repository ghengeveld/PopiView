[app:popiview]
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
cfg>>urlmap>>keywordcloud.json = keywordcloud
cfg>>urlmap>>hitmonitor.json = hitmonitor
cfg>>urlmap>>dummydata = dummydata
cfg>>urlmap>>randomdata = randomdata
cfg>>urlmap>>cleardata = cleardata
cfg>>urlmap>>component = get_component

cfg>>sparams>>google = q
cfg>>sparams>>bing = q
cfg>>sparams>>yahoo = p

[filter:pdb]
use = egg:z3c.evalexception#ajax

[pipeline:main]
pipeline = pdb popiview

[server:main]
use = egg:PasteScript#wsgiutils
host = ${debug.ini:host}
port = ${debug.ini:port}
