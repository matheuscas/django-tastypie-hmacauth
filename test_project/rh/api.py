# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.resources import Resource, ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.exceptions import Unauthorized
from tastypie.authentication import SessionAuthentication, Authentication
from tastypie import fields
from tastypie.api import Api
from datetime import datetime
from rh.models import Patrao, Funcionario
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


class PatraoResource(ModelResource):
    usuario = fields.ForeignKey(UserResource, 'usuario', null=True)
    class Meta:
        queryset = Patrao.objects.all()
        resource_name = 'patrao'
        filtering = {
            'usuario': ALL_WITH_RELATIONS,
        }
        authentication = HMACAuthentication()
        authorization = Authorization()

class FuncionarioResource(ModelResource):
    usuario = fields.ForeignKey(UserResource, 'usuario', null=True)
    patrao = fields.ForeignKey(PatraoResource, 'patrao', null=True)
    class Meta:
        queryset = Funcionario.objects.all()
        resource_name = 'funcionario'
        filtering = {
            'usuario': ALL_WITH_RELATIONS,
        }
        authentication = HMACAuthentication()
        authorization = Authorization()

v1_api = Api(api_name='v1')
v1_api.register(PatraoResource())
v1_api.register(FuncionarioResource())
v1_api.register(UserResource())

