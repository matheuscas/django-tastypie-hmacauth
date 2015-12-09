.. image:: https://travis-ci.org/matheuscas/django-tastypie-hmacauth.svg?branch=master
    :target: https://travis-ci.org/matheuscas/django-tastypie-hmacauth

Django-tastypie-hmacauth
------------------------

This module provides HMAC authentication service for Tastypie APIs. It tries to mimic the `Amazon Web Services Security Model (Signature 2) <http://aws.amazon.com/articles/1928>`_ with some modifications based on `this discussion <http://www.thebuzzmedia.com/designing-a-secure-rest-api-without-oauth-authentication/>`_.

Dependencies
------------

This project relies on two main dependencies:

- Django 1.6 or higher
- Tastypie 0.12.2 or higher

This project **will not install Django for you** despite of to be a dependency. But, it will install Tastypie, at least. 

Installation
------------

.. code-block:: python

   pip install django-tastypie-hmacauth==0.0.1b7

And you are done! You just need to import do your *api.py* and you along with your *ModelResources* and make a little modification in *settings.py*. See 'Caveats'. 

Usage
-----

Borrowed from `django-tastypie-oauth <https://github.com/orcasgit/django-tastypie-oauth>`_. 

When you create your Tastypie resources, use `HMACAuthentication` like so:

.. code-block:: python

    # mysite/polls/api.py
    from tastypie.resources import ModelResource
    from tastypie.authorization import DjangoAuthorization
    from polls.models import Poll, Choice
    from tastypie import fields
    from tastypie_hmacauth import HMACAuthentication

    class ChoiceResource(ModelResource):
        class Meta:
            queryset = Choice.objects.all()
            resource_name = 'choice'
            authorization = DjangoAuthorization()
            authentication = HMACAuthentication()

    class PollResource(ModelResource):
        choices = fields.ToManyField(ChoiceResource, 'choice_set', full=True)
        class Meta:
            queryset = Poll.objects.all()
            resource_name = 'poll'
            authorization = DjangoAuthorization()
            authentication = HMACAuthentication()

Making GET requests
~~~~~~~~~~

- Define your <URL>
 - http://<HOST>[:PORT]<API_ENDPOINT>?your_custom_parameter=value&public_key=public_user_id&timestamp=timestamp_value

- Hash URL with HMAC and SHA256 (example with Python)

.. code-block:: python

     key = hmac.new(SECRET_KEY, <URL>, hashlib.sha256)
     api_key_value = key.hexdigest()

- You final URL will be:
 - http://<HOST>[:PORT]<API_ENDPOINT>?api_key=api_key_value&custom_parameter=value&public_key=public_user_id&timestamp=timestamp_value
 

Making POST requests
~~~~~~~~~~

- Define your <URL>
 - http://<HOST>[:PORT]<API_ENDPOINT>?your_custom_parameter=value&public_key=public_user_id&timestamp=timestamp_value
 
- Attach your payload data as string to your URL
 - <PAYLOAD> = "{'key':'value', 'key_1': 'value_1'}"
 - http://<HOST>[:PORT]<API_ENDPOINT>?your_custom_parameter=value&public_key=public_user_id&timestamp=timestamp_value<PAYLOAD>

- Hash URL with HMAC and SHA256 (example with Python)

.. code-block:: python

     key = hmac.new(SECRET_KEY, <URL>, hashlib.sha256)
     api_key_value = key.hexdigest()

- You final URL will be:
 http://<HOST>[:PORT]<API_ENDPOINT>?api_key=api_key_value&custom_parameter=value&public_key=public_user_id&timestamp=timestamp_value

Caveats
-------

.. code-block:: python

     from django.contrib.auth.models import User
     from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
     from tastypie.authorization import Authorization
     from tastypie_hmacauth import HMACAuthentication

     class UserResource(ModelResource):
        class Meta:
            queryset = User.objects.all()
            resource_name = 'usuario'
            excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
            filtering = {
               'username': ALL,
               'id' : ['exact'],
            }
            authentication = HMACAuthentication()
            authorization = Authorization()


Using HMAC in this way let ours requests pure and simple, without any sensible information attached, such as passwords. However, if we always need a *public_key* that refers to a valid user id, how can we create a new user using Django User model? For example, you have a feature to create a new user to your service, but you can't do that without having the user's id. Tricky, right? So, it came an ideia to create another secret key, called SECRET ID based on the original SECRET KEY, hashing it with itself. Hence, both client and server knows about it and you can send the hashed value along with public key parameter. HMACAuthentication will see that this is a high level request and won't validate the user for you. 

But **remember**: use the SECRET ID only for this situation, because use it in all scenarios will really open your API to severe attacks. 

Then, to **HMACAuthentication** fully works with Tastypie and Django and provide HMAC authentication to your API, you have to change your *settings.py* like bellow:

.. code-block:: python

   import hmac
   import hashlib 
  
   # SECURITY WARNING: keep the secret key used in production secret!
   SECRET_KEY = 'YOUR SECRET KEY' #it could be the default generated by Django

   digest_maker = hmac.new(SECRET_KEY, SECRET_KEY, hashlib.sha256)
   SECRET_ID = digest_maker.hexdigest() 

**Sorry for that. In the next releases, it will let you decide what to do.**
**Also, the above code is a suggestion. SECRET_ID can be any value of your choice.**

**NOTE**: You should be aware of your parameters ordering. This authentication method removes API_KEY from URL and reconstructs it sorting the parameters in ascending order to validate request. Hence, you **MUST** sort your params as well.

How HMAC authentication works
------------

TL;DR:
~~~~~~~~~~
Server and client holds a SECRET key each one. This SECRET key will be used to hash every HTTP request, with sha256, sent by client and this hash is sent with the request as well - we called **api_key**. The server takes everything but *api_key* and does the same as client did. If the SERVER's hash matches with CLIENT's hash, we are good to go. Otherwise, the request will be revoked. 

Step by step process
~~~~~~~~~~~~~~~~~~~~
| 1 - **[CLIENT]** Before making the REST API call, it combines a bunch of unique data together. This module takes the whole URL with all eventual params. Example: *http://host:port/api/v1/entry/?param1=value1&param2=value2*. 

| 2 - **[CLIENT]** Hash (SHA256) the blob of data with your private key assigned to you by the system.

| 3 - **[CLIENT]** Send the server the following data:
 
- Some user-identifiable information like client ID, user ID or something else it can use to identify who you are. Here, we call it **public_key**. This is the public API key, never the private API key. This is a public value that anyone (even evil masterminds can know and you don’t mind). It is just a way for the system to know WHO is sending the request, not if it should trust the sender or not (it will figure that out based on the HMAC).

- Attach a timestamp of time (**in UTC, following this format: %Y-%m-%dT%H:%M:%S**) kind along with the request so the server can decide if this is an “old” request, and deny it. The timestamp must be included into the HMAC generation. The only way to protect against "`replay attacks <https://en.wikipedia.org/wiki/Replay_attack>`_". 

- Attach the HMAC (hash) that you generated with your request.

- Send all the data (parameters and values) you were planning on sending anyway. Probably unencrypted if they are harmless values, like we showed at the Step #1 or other operating nonsense. If the values are private, you’ll need to encrypt them, like a password. 

- The final regular request will be something like this: 

*http://host:port/api/v1/entry/?api_key=your_hash&public_key=public_user_value&others_params=others_values&timestamp=utc_time*

**IMPORTANT: Including 'api_key', the parameters MUST be sorted by alphabetic order**

| 4 - **[SERVER]** Receive all the data from the client.

| 5 - **[SERVER]** Compare the current server’s timestamp to the timestamp the client sent. Make sure the difference between the two timestamps it within an acceptable time limit. We set 5 minutes by default. However, you can easily change this.

| 6 - **[SERVER]** Using the user-identifying data sent along with the request (public_key) look the user up in the DB and checks if is a valid user.

| 7 - **[SERVER]** Re-combine the same data together in the same way the client did it. Then hash (generate HMAC) that data blob using the SECRET key. Remember to include the timestamp from the client in the HMAC re-calculation on the server. Since you already determined this timestamp was within acceptable bounds to be accepted, you have to re-apply it to the hash calculation to make sure it was the same timestamp sent from the client originally, and not a made-up timestamp from a `man-in-the-middle attack <https://en.wikipedia.org/wiki/Man-in-the-middle_attack>`_.

| 8 - **[SERVER]** Run that mess of data through the HMAC hash, exactly like it did on the client. 

| 9 - **[SERVER]** Compare the hash you just got on the server, with the hash the client sent you; if they match, then the client is considered legit, so process the command. Otherwise reject the command!

REMEMBER
~~~~~~~~
Your private key should **NEVER EVER** be transferred over the wire, it is just used to generate the HMAC, the server looks the private key back up itself and recalculates its own HMAC. 
