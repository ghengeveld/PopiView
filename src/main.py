import cherrypy
import smtplib
from datetime import datetime
from email.MIMEText import MIMEText
import logging

logger = logging.getLogger('popiview')


def load_image():
    img = open('img.gif', 'r')
    try:
	return img.read()
    finally:
    	img.close()


class Main:
    image_data = load_image()

    @cherrypy.expose
    def index(self):
        return "hi"

    def logHit(self, cur=None, ref=None):
        msg = MIMEText("Date: %s\nIP: %s\nCUR: %s\nREF: %s" % (
            datetime.utcnow(),
            cherrypy.request.remote.ip,
            cur, ref))

        msg['Subject'] = "Hit"
        msg['From'] = "Gert Hengeveld <info@ghengeveld.nl>"
        msg['To'] = "gert@infrae.com"
        
        s = smtplib.SMTP()
        s.connect("smtp.xs4all.nl")
        s.helo()
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.close()
        
        return "logged"

    @cherrypy.expose("image.gif")
    def image(self, cur=None, ref=None):
        cherrypy.response.headers['Content-Type'] = "image/gif"
        cherrypy.response.headers['Expires'] = "Sat, 26 Jul 1997 05:00:00 GMT"
        cherrypy.response.headers['Cache-Control'] = "no-cache, must-revalidate"
        
        #self.logHit(cur=cur, ref=ref)        
        return image_data

cherrypy.quickstart(Main())
