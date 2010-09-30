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
* timestamp

Using this data we can construct a Hit object, 

>>> from popiview.hit import Hit
>>> hit = Hit(u'http://mysite.com/page')
>>> hit.url()
u'http://mysite.com/page'

A hit object normalizes the url, so it can strip of the slash at 
the end of the url. 

>>> hit = Hit(u'http://mysite.com/page/')
>>> hit.url()
u'http://mysite.com/page'

There is an option to remove 'www' subdomains from the url

>>> hit = Hit(u'http://www.mysite.com/page/', remove_www=True)
>>> hit.url()
u'http://mysite.com/page'

The referrer string can also be passed to the hit class, which will
be analyzed to see if there are interesting keywords.

>>> hit = Hit(u'http://www.mysite.com/page', 
...           referrer='http://searchengine.com?q=cool%20page')
>>> hit.keywords()
[u'cool', u'page']

It is also possible to specify a datetime when the request was made.
This is useful in unittesting, and to add historic data from external 
sources like google-gdata

>>> hit = Hit(u'http://www.mysite.com/page', timestamp=1285689362)

The timestamp should be a unix timestamp of UTC time.


Storing Hits
------------

Hits need to be stored, so we can sum them and analyse them over time.
We first create a storage object

>>> from popiview.storage import MemoryStorage
>>> storage = MemoryStorage()

Adding a hit is quite simple:

>>> storage.add_hit(Hit(u'http://www.mysite.com/page'))

We can retrieve a list of all pages accessed

>>> storage.list_urls()
[u'http://www.mysite.com/page']

Lets add another hit from a while ago

>>> storage.add_hit(Hit(u'http://www.mysite.com/page2',
...                     timestamp=1285600000))

Now we should have two urls stored

>>> storage.list_urls()
[u'http://www.mysite.com/page', u'http://www.mysite.com/page2']

We can also ask the storage for a list of urls that have been
accessed within a certain period. This should return only our first entry, 
because the other one had an older timestamp.

>>> storage.list_urls(start_time=1285600100)
[u'http://www.mysite.com/page']

Lets empty the hit log now and create some dummy hits with different timestamps

>>> storage.clear_hits()
>>> storage.add_hit(Hit(u'http://www.mysite.com/page', timestamp=1285050010,
...                     referrer='http://google.com?q=cool%20page'))
>>> storage.add_hit(Hit(u'http://www.mysite.com/page', timestamp=1285060010,
...                     referrer='http://google.com?q=cool'))
>>> storage.add_hit(Hit(u'http://www.mysite.com/page', timestamp=1285070010,
...                     referrer='http://google.com?q=page'))

We can now get the number of hits on that page for a specific period

>>> storage.get_hitcount(u'http://www.mysite.com/page',
...                  start_time=1285050000,
...                  end_time=1285070000)
2

We can also get an overview of all urls and their hitcounts

>>> storage.get_hitcounts(start_time=1285050000, end_time=1285070000)
{u'http://www.mysite.com/page': 2}

It's also possible to get the keywords for a specific page within a 
certain period

>>> storage.get_keywords(u'http://www.mysite.com/page',
...                      start_time=1285050000,
...                      end_time=1285070000)
{u'page': 1, u'cool': 2}


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

>>> from popiview.analyzer import Analyzer
>>> analyzer = Analyzer(storage, start_time=0, boundary_time=5000,
...                     end_time=10000)

Now that we have the analyzer, we can ask it what the trends are
on the website. First we will need to create some dummy data.

>>> from popiview.dummy import Dummy
>>> dummy = Dummy(storage)
>>> dummy.create_hits_linear(u'http://www.mysite.com/page',
...                          start_time=0, end_time=10000,
...                          start_hits_per_hour=0, end_hits_per_hour=50,
...                          referrer='http://google.com?q=cool%20page')
>>> storage.list_urls(unique=True)
[u'http://www.mysite.com/page']

Add some more dummy data

>>> dummy.create_hits_linear(u'http://www.mysite.com/page',
...                          start_time=5000, end_time=10000,
...                          start_hits_per_hour=0, end_hits_per_hour=50,
...                          referrer='http://google.com?q=cool')
>>> dummy.create_hits_linear(u'http://www.mysite.com/page2',
...                          start_time=0, end_time=10000)
>>> dummy.create_hits_linear(u'http://www.mysite.com/page3',
...                          start_time=0, end_time=10000,
...                          start_hits_per_hour=0, end_hits_per_hour=75)
>>> dummy.create_hits_linear(u'http://www.mysite.com/page4',
...                          start_time=0, end_time=10000,
...                          start_hits_per_hour=200, end_hits_per_hour=0)

Now we can test the analyzer

>>> analyzer.get_top_deviators(limit=1)
[{'url': u'http://www.mysite.com/page2',
  'value: 0.25,
  'keywords': {'cool': 1, 'page': 1}]

