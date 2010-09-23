
PopiView
========

In this document we will describe the PopiView API from a birdseye perspective.
The goal of PopiView is to monitor the current popularity of a webpage 
in respect to the historical popularity.

Hits
----

When a user visits a page, we retrieve the following data:

* url of page
* referrer 
* user-agent
* timestamp

Using this data we can construct a Hit object, 

>>> from popiview import Hit
>>> hit = Hit('http://mysite.com/page')
>>> hit.url()
u'http://mysite.com/page'

A hit object normalizes the url, so it can strip of the slash at 
the end of the url. 

>>> hit = Hit('http://mysite.com/page/')
>>> hit.url()
u'http://mysite.com/page'

There is an option to remove 'www' subdomains from the url

>>> hit = Hit('http://www.mysite.com/page/', remove_www=True)
>>> hit.url()
u'http://mysite.com/page'

The referer string can also be passed to the hit class, which will
be analyzed to see if there are interesting keywords.

>>> hit = Hit('http://www.mysite.com/page/', 
...            referrer='http://searchengine.com?q=cool%20page')
>>> hit.keywords()
[u'cool', u'page']

The user-agent string can be added so we can determine if this request
was made by a bot. The code contains a listing of common bots.

>>> hit = Hit('http://www.mysite.com/page/', 
...            user_agent='Googlebot')
>>> hit.is_bot()
True

It is also possible to specify a datetime when the request was made.
This is useful in unittesting, and to add historic data from external 
sources like google-gdata

>>> hit = Hit('http://www.mysite.com/page/', 
...            when='2010-01-01T12:12:12')

The datetime string is always in UTC time.


Storing Hits
------------

Hits need to be stored, so we can sum them and analyse them over time.
We first create a storage object

>>> from Popiview import InMemoryStorage
>>> storage = InMemoryStorage()

Adding a hit is quite simple:

>>> storage.add_hit(hit)

Let's add another hit

>>> storage.add_hit(Hit('http://www.mysite.com/page/'))

And add another hit from a while ago

>>> storage.add_hit(Hit('http://www.mysite.com/page/',
...                     when='2010-01-01T20:19:53'))

We can now ask the storage for a list of urls that have been
accessed within a certain period.

>>> storage.urls_accessed(start_time=23454325, 
...                       minimal_hits=5)
['http://www.mysite.com/page/']

These page urls are the ones that we are actually interested in.
We can now get the number of hits on that page for a specific period

>>> storage.hit_count('http://www.mysite.com/page/',
...                   start_time=23454325,
...                   end_time=234234423)
3

It's also possible to get the keywords for a specific page within a 
certain period

>>> storage.hit_keywords('http://www.mysite.com/page/',
...                      start_time=23454325,
...                      end_time=234234423)
{'page': 1, 'cool': 1}

Determining Popularity
----------------------

Let's analyze the storage with all its hits.
To create an Analyzer instance, we need to pass
a storage instance.

An analyzer looks at the hits for a page within
a certain period, and compares those numbers with 
the history of that page.

For example, if we want to analyze all hits for a 
single day, and compare them with hits from the last
month, we can set `short_term_max` to yesterday and 
`long_term_max` to 1 month.

What the analyzer does is:

- Ask the storage for a list of urls that were accessed in the
  short term period, optionally giving a treshold
- For each of these urls, get the number of hist from both the
  short term and the long term period
- Hand of these numbers to (one of) the popularity_algorithm(s)

>>> from popiview import Analyzer
>>> analyzer = Analyzer(storage,
                        short_term_min=<<1 hour>>,
                        short_term_max=<<1 day>>,
                        long_term_max=<<1 month>>)

Now that we have the analyzer, we can ask it what the trends are
on the website.

>>> analyzer.get_movers_and_shakers()
[{'url':'http://www.mysite.com/page/',
  'value: 0.25,
  'keywords': {'cool': 1, 'page': 1}]

