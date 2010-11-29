import os
from optparse import OptionParser
from paste.deploy import appconfig
from popiview.server import ConfigParser
from popiview.storage import SQLStorage

parser = OptionParser(description="Clean up old database records.")
parser.add_option(
    "--config-file", dest="config_file",
    help="path to settings.ini or another config file")
parser.add_option(
    "--days", dest="days", default="7",
    help="specify cleanup of records which are at least * days old")


def cleanup():
    options, args = parser.parse_args()
    if not options.config_file:
        print "Required option: --config-file"
        exit(1)
    if not os.path.isfile(options.config_file):
        print "Invalid value for option --config-file"
        exit(1)
    config = appconfig('config:' + options.config_file, relative_to=os.getcwd())
    config = ConfigParser(config)
    storage = SQLStorage(config)
    storage.clear_hits(int(options.days))
