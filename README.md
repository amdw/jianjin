# Introduction

Jianjin is a web application designed to help manage Chinese vocabulary.

When learning a language, it is common to need to scribble down notes about new words you discover: definitions, example sentences, contrasts with other similar words, memory aids and so forth. These notes are far more useful for students than most dictionaries; however, too often, they get lost on bits of paper and in the margins of textbooks, never to be read again.

Also, there are exams such as [the HSK](http://en.wikipedia.org/wiki/Hanyu_Shuiping_Kaoshi), which require students to memorise specific lists of vocabulary. The HSK textbooks contain the full word lists, but these include English definitions and example sentences, and are not particularly useful for self-tests.

A language like Chinese, which does not use the Roman alphabet, imposes additional challenges on non-native learners. The [Pinyin](http://en.wikipedia.org/wiki/Pinyin) transcription system exists for Mandarin, but at a certain stage, it can become an impediment to learning to read characters: if your notes have both characters and Pinyin, the temptation to read the Pinyin and ignore the characters is very strong, in which case you will not build up practice in reading characters. However, if you do not write down the Pinyin, it can be time-consuming to look it up if you cannot remember it, because you have to look up the characters by radical in a dictionary, or write the character into an OCR system such those available on modern mobile devices.

Ideally what you want is the ability to turn Pinyin on and off in your notes at will.

A web application backed by a database can help address all these problems. Jianjin is designed to:

* Store words as you learn them, with definitions, example sentences, contrasts to other words, and miscellaneous notes
* Tag words so that you can confine your study to particular word sets of interest, such as the vocabulary lists for HSK exams, while still allowing you to keep all your vocabulary notes in one place
* Turn Pinyin on and off at will, so you can decide what formats are most helpful at your stage of learning
* Test yourself by being presented with a random "flash card", and keep track of which words you find most difficult so you can focus on those

Jianjin is designed to work on both desktop and mobile browsers so you can revise and take notes wherever you are.

The name "Jianjin" comes from a Chinese idiom: [循序渐进](http://www.mdbg.net/chindict/chindict.php?page=worddict&wdrst=0&wdqb=%E5%BE%AA%E5%BA%8F%E6%B8%90%E8%BF%9B) (xúnxùjiànjìn), meaning "to make steady progress incrementally".

I wrote this software because I want to use it, and because I wanted to practice writing a modern JavaScript-based web application. I would be very grateful to anyone who can suggest ways I could do things better!

# Current status

This software is currently still incomplete and should be considered to be in pre-alpha state. The interface is still changing a lot, and the data model is not yet fully developed. I apologise that this isn't much use yet, but I believe in [releasing early and often](http://www.catb.org/esr/writings/homesteading/cathedral-bazaar/ar01s04.html)!

# Installing and running

Jianjin is designed to be easily deployed on any [PaaS](http://en.wikipedia.org/wiki/Platform_as_a_service) which supports [Python](http://www.python.org/) and [Django](http://djangoproject.com/). The configuration files included here are designed for [Heroku](http://heroku.com/), but moving it to a different PaaS should require just a few configuration changes in ```jianjin/settings.py```.

## Local computer

For development or personal local use, you can run Jianjin on your own computer; this is probably the easiest way to try it out. (The following instructions assume a Unix-like environment, such as Linux or Mac OS X. There's no reason it shouldn't be possible to run this on Windows as well by similar means, but I haven't tried it.)

* Install Python and virtualenv as described in [this guide](http://install.python-guide.org/)
* Install the Heroku toolbelt as described in [this guide](https://devcenter.heroku.com/articles/getting-started-with-python#local-workstation-setup)
* Install [Postgres](http://www.postgresql.org/) and ensure that the ```bin``` directory (containing ```pg_config```) is on your ```PATH```
* Clone this Git repository and ```cd``` into it
* Create a virtualenv: ```virtualenv venv```
* Activate the virtualenv: ```source venv/bin/activate```
* Install the Django toolbelt and the other required Python libraries into your virtualenv: ```pip install -r requirements.txt```
* Create a ```.env``` file with local settings: ```cp env.sample .env```. Edit the ```DATABASE_URL``` in the new ```.env``` file to point to a suitable path for your SQLite database.
* Set up the database and an admin user: ```foreman run python manage.py syncdb```
* Start the local development server: ```foreman start```

You should get a log message telling you what port the server has bound to; you can then visit localhost:port in your browser and the page should load.

Note that if you want to run Django commands, e.g. using the ```manage.py``` interface, you will need to prefix them with ```foreman run``` in order to pull in the necessary configuration from the ```.env``` file. For example, if you want to run the Django development server rather than Gunicorn, you need to run ```foreman run python manage.py runserver```, or to run a Django shell, ```foreman run python manage.py shell```, etc.

### Running JavaScript tests

If you want to run the JavaScript tests, you will need to do the following:

* Install [Node.JS](http://nodejs.org/)
* Install [Bower](http://bower.io/) using ```npm install -g bower```
* Run ```npm install``` in the root directory of the project; this will download some additional Java libraries for local testing
* Run ```npm test```

## Deploying to Heroku or other PaaS

Running Jianjin on the public Internet is much more useful than running it on a private computer, as it gives you access to the application and all your data from anywhere on any web-enabled device.

However, running any web application on the public Internet imposes stricter requirements than running it on a private computer, largely due to security considerations.

Any secret information, such as database passwords or the Django ```SECRET_KEY```, must *not* be included in any file checked into version control; instead, they must be set privately for each instance of the application through a mechanism such as Heroku's [config vars](https://devcenter.heroku.com/articles/config-vars). These also provide a useful mechanism for non-secret configuration information which can vary between deployments (such as a test site versus production).

In addition, if you want your deployment to be at all secure, you must [use SSL](https://devcenter.heroku.com/articles/ssl-endpoint) to ensure that all communications between browser and server are encrypted. Any use of regular unencrypted HTTP will make your deployment insecure. If you don't consider your Jianjin data to be private, you may not mind this, but you must be fully aware of the consequences: your Django username, password and private session data can be easily intercepted, especially on public mobile or Wifi networks, giving anyone the ability to impersonate you to the web application and thereby do anything you have the power to do within Jianjin.

A full checklist of things to consider when deploying Django applications on the Internet may be found [on the Django website](https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/). I have tried to take care of as many items on this checklist as possible in the way this application is configured and in the below instructions, but you are solely responsible for the security of your own deployments.

(Thanks very much to Github user michaelmior for [some useful patterns](https://github.com/michaelmior/heroku-django-skeleton) for Django on Heroku.)

The following instructions are specific to Heroku; to deploy to other PaaS services, consult the documentation for those services. The instructions are based on [the Heroku Django tutorial](https://devcenter.heroku.com/articles/getting-started-with-django), so you should check there and elsewhere in the Heroku documentation if this doesn't work.

* Create a [Heroku account](http://heroku.com/), if you don't already have one, and run ```heroku login```
* Run ```heroku create``` to create a new Heroku application
* Run ```jianjin/heroku-configure.py``` to set certain required configuration properties, such as generating a Django secret key
* Run ```git push heroku master``` to push your current code to Heroku
* Run ```heroku run python manage.py syncdb``` to set up the database

Assuming all this worked, you should be able to run ```heroku open``` to open up the application.

# Architecture

Jianjin uses [Angular.JS](http://angularjs.org/) for the front end user interface, with the back-end RESTful JSON API being implemented in Python using [Django](http://djangoproject.com/).

I chose these technologies because I wanted to learn more about them by using them for "real work", not because I necessarily think they are best-in-class. I'm still developing my opinions on that as I go.

# Licensing

## Preamble

In theory, Jianjin could be used as part of a public online service. However, this is not something I am interested in doing myself at the moment.

I want to make this software freely available for other Chinese learners to use; however, I do not want anyone to turn it into a proprietary for-profit service without giving me anything in return. I am therefore making it available under [the GNU Affero GPL](http://www.gnu.org/licenses/why-affero-gpl.html) or AGPL, a [copyleft](http://en.wikipedia.org/wiki/Copyleft) [open source](http://opensource.org/) license. The AGPL can be read in the LICENSE file in this repository.

As an open source license, the AGPL allows the software to be used, redistributed, and/or modified freely for any purpose. However, as a copyleft license, it requires that if any modified versions are distributed, they must be made freely available under the terms of the same license. In addition, the AGPL (in contrast to the regular GPL) requires that if modified versions of the software are run on any network server, the modified source code must also be made available to the users under the AGPL.

This ensures that if anyone does incorporate this software into an online service, any improvements they make must also be made available as free software.

I am prepared to consider requests to dual-license parts of this software. Some parts may be useful to people who want to write similar web applications but do not want to release their code under the AGPL, and I am keen to support other open source software where possible. Any such requests should be emailed to github@medworth.org.uk. You should explain which parts you want to use and how.

## Copyright

All files in this repository are Copyright (C) 2014 Andrew Medworth, except where otherwise stated in individual files.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see [the GNU website](http://www.gnu.org/licenses/).

# Contributing

I am happy to receive pull requests. However, I am quite busy, so I apologise in advance if your request does not receive timely attention.

I will probably accept pull requests which I consider to improve the functionality of the software without creating undue maintenance burdens.

However, I wrote this application primarily for myself, to help with my *Chinese* studies. As such, I am unlikely to accept pull requests to make the application work for other languages, unless it is very clear that the change would not cause any problems for the Chinese functionality. If you want to make such modifications, please feel free to create a fork.

# My personal database

My own personal database of Chinese words is not something I intend to make publicly available at the moment.

Apologies for any disappointment; however, in order for Jianjin to be maximally useful as a learning tool, I believe you need to enter words into the system yourself as you learn.
