CREATE TABLE IF NOT EXISTS `hits` (
  `hit_id` int(32) NOT NULL AUTO_INCREMENT,
  `hit_timestamp` int(32) NOT NULL,
  `hit_url` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `hit_path` varchar(500) COLLATE utf8_unicode_ci NOT NULL,
  `hit_referrer` varchar(2000) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`hit_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=710 ;

CREATE TABLE IF NOT EXISTS `hits_keywords` (
  `hit_id` int(32) NOT NULL,
  `keyword` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`hit_id`,`keyword`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
