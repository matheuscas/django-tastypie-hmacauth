Django-tastypie-hmacauth
------------------------

This module provides HMAC authentication services for Tastypie APIs. It tries to mimic the `Amazon Web Services Security Model (Signature 2) <http://aws.amazon.com/articles/1928>`_ with some modifications based on `this discussion <http://www.thebuzzmedia.com/designing-a-secure-rest-api-without-oauth-authentication/>`_.

Dependencies
------------

This project relies on two only dependencies:

- Django 1.6 or higher
- Tastypie 0.12.2 or higher

This project **will not install Django for you** despite of to be a dependency. But, it will install Tastypie for you. 

Installation
------------

.. code-block:: python

   pip install django-tastypie-hmacauth

And you are done! There is no need to change anything on Django settings (except for only one situation that we will talk about soon). Just import and use it.
