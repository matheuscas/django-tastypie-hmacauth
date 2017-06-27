from __future__ import unicode_literals
import hmac
import hashlib
import time
from datetime import datetime

from django.conf import settings
from tastypie.http import HttpUnauthorized
from tastypie.compat import get_user_model
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse
import pprint, operator

class HMACAuthentication(Authentication):
    """A keyed-hash message authentication for Tastypie and Django"""
    
    def __init__(self, require_active=True, timestamp_window=5):
        self.require_active = require_active
        self.timestamp_window = timestamp_window

    def _unauthorized(self):
        return HttpUnauthorized()

    def extract_credentials(self, request):
        public_key = request.GET.get('public_key') or request.POST.get('public_key')
        if public_key is None:
            raise ImmediateHttpResponse(response=http.HttpBadRequest('public_key not found'))
        
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        if api_key is None:
            raise ImmediateHttpResponse(response=http.HttpBadRequest('api_key not found'))

        timestamp = request.GET.get('timestamp') or request.POST.get('timestamp')
        if timestamp is None:
            raise ImmediateHttpResponse(response=http.HttpBadRequest('timestamp not found'))

        return public_key, api_key, timestamp

    def is_authenticated(self, request, **kwargs):
        
        try:           
            public_key, api_key, timestamp = self.extract_credentials(request)
            if not self.is_api_key_valid(api_key, request) or \
                not self.check_active(self.get_user(public_key)) or \
                    not self.is_timestamp_valid(timestamp):
                        return False

        except Exception, e:  
            return False

        return True    

    def is_api_key_valid(self, api_key, request):

        protocol = 'http://'
        if 'https' in request.scheme:
            protocol = 'https://'

        host = request.META['HTTP_HOST'] if 'HTTP_HOST' in request.META else 'localhost' #ResourceTestCase api_client does not setn HTTP_HOST
        path = request.META['PATH_INFO']

        params = request.GET.copy()
        params = sorted(params.items(), key=operator.itemgetter(0))
        query_string = '?'
        for t in params:
            if t[0] != 'api_key':
                query_string = query_string + t[0] + '=' + t[1] + '&'
                
        url = protocol + host + path + query_string
        url = url[:len(url) - 1]
        if request.method == 'POST' or request.method == 'PUT' or request.method == 'PATCH':
            url += request.body.decode('utf-8')
        digest = hmac.new(settings.SECRET_KEY, url.encode('utf-8'), hashlib.sha256).hexdigest()
        if digest != api_key:
            raise ImmediateHttpResponse(response=http.HttpBadRequest('api_key is not valid'))
        return True

    def get_user(self, public_key):
        
        if public_key == settings.SECRET_ID:
            self.require_active = False
            return True

        User = get_user_model()
        try:
            user = User.objects.get(pk=public_key)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()
        return user

    def is_timestamp_valid(self, timestamp):
        """Timestamp must be string in %Y-%m-%dT%H:%M:%S. format """

        try:
            timestamp_server = datetime.utcnow()
            timestamp_client = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

            d1_ts = time.mktime(timestamp_client.timetuple())
            d2_ts = time.mktime(timestamp_server.timetuple())

            diff = int(d2_ts-d1_ts) / 60

            if diff > self.timestamp_window:
                raise ImmediateHttpResponse(response=http.HttpBadRequest('Exceeded timestamp window'))
        except Exception, e:            
            raise ImmediateHttpResponse(response=http.HttpBadRequest('Unknown error on timestamp validation'))

        return True    

