# Description

This is a simple web site for scheduling appointments for mikvah.

It's meant to be very easy to use and privacy sensitive. It encourages scheduling appointments close together, but not too many to handle. It prevents scheduling appointments before the zman. Shabbes works slightly differently, first come first served starting at the zman. It supports sms confirmations via twilio.

You'll need to make simple changes to the source code for your own: time zone, geographic location, payment site, and appointment rate.

This software does not currently support direct integration of payment processing. You can link to an existing payment page.

# HOWTO sketch

All you need is support for python and django.

To set it up, you're going to want to be familiar with django, or go through [its tutorial](https://docs.djangoproject.com/en/4.2/intro/tutorial01/). Start a project and wire in this code as an app. Migrate its database schema, and ideally make its images available as a static web pages. (This may be as easy as copying from the mikvah/static directory to your site's static directory.) Install "julian" and "zmanim" and optionally "twilio" via pip. Make sure TIME_ZONE is correct in settings.py.

Consider using https://pythonanywhere.com or https://fly.io to serve up the site for free, since it should be pretty light. Keep portability by [registering](https://www.namecheap.com/domains/) and serving your own domain name. If you don't have any tech person to help with this stuff, consider instead a hosted solution like mikvahcloud or mikvahrsvp.

There are really only three entry points:

* /mikvah - for scheduling appointments, first of three steps to book an appointment
* /mikvah/admin - django admin
* /mikvah/admin/attendant - for viewing appointments

![screenshot](./mikvahFirstScreen.png)
