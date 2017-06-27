#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import hmac
import hashlib
import json
from datetime import datetime
from django.conf import settings
from django_nose.tools import assert_code
from django.core import management
from django.contrib.auth.models import User
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from test_project.wsgi import application as app
from autofixture import AutoFixture
from rh.models import Patrao, Funcionario

funcionarios = '/api/v1/funcionario/'
patroes = '/api/v1/patrao/'
usuarios = '/api/v1/usuario/'

QTD_PATROES = 1
PREFIX = 'http://localhost'
PREFIX_SSL = 'https://localhost'
TEST_USERNAME = "novo_usuario_teste"
TEST_PASSWORD = "novo_usuario_senha"

TIMESTAMP_ANTIGO = "2015-08-17T10:10:10"
TIMESTAMP_AGORA = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

def setup_module():
    test_user = User.objects.create_user(username='test_user',password='pass',email='email@email.com')
    test_user.save()
    test_user_2 = User.objects.create_user(username='test_user_2',password='pass',email='email2@email.com')
    test_user_2.save()
    fixture = AutoFixture(Patrao, field_values={'usuario': test_user_2})
    fixture.create(QTD_PATROES)


def hmac_hashing(url, payload=None, ssl_on=False):

    url_to_hash = PREFIX + url if not ssl_on else PREFIX_SSL + url
    if payload:
        url_to_hash += json.dumps(payload)
    digest_maker = hmac.new(settings.SECRET_KEY, url_to_hash, hashlib.sha256)
    digest = digest_maker.hexdigest()
    if 'public_key' in url:
        url = url + "&api_key=" + digest
    else:
        url = url + "?api_key=" + digest
    return url

def get(url_get, hashing=True, ssl_on=False):

    environ = {}
    if ssl_on:
        environ["wsgi.url_scheme"] = "https"

    if hashing:
        url_get = hmac_hashing(url_get, ssl_on=ssl_on)

    c = Client(app, BaseResponse)
    return c.get(url_get, environ_overrides=environ)

def post(url_post, payload, hashing=True, ssl_on=False):

    environ = {}
    if ssl_on:
        environ["wsgi.url_scheme"] = "https"

    if hashing:
        url_post = hmac_hashing(url_post, payload, ssl_on=ssl_on)
    c = Client(app, BaseResponse)
    return c.post(url_post, data=json.dumps(payload), headers={'Content-Type':'application/json'}, environ_overrides=environ)

def put(url_put, payload, hashing=True, ssl_on=False):

    environ = {}
    if ssl_on:
        environ["wsgi.url_scheme"] = "https"

    if hashing:
        url_put = hmac_hashing(url_put, payload, ssl_on=ssl_on)
    c = Client(app, BaseResponse)
    return c.put(url_put, data=json.dumps(payload), headers={'Content-Type':'application/json'}, environ_overrides=environ)

def patch(url_patch, payload, hashing=True, ssl_on=False):

    environ = {}
    if ssl_on:
        environ["wsgi.url_scheme"] = "https"

    if hashing:
        url_patch = hmac_hashing(url_patch, payload, ssl_on=ssl_on)
    c = Client(app, BaseResponse)
    return c.patch(url_patch, data=json.dumps(payload), headers={'Content-Type':'application/json'}, environ_overrides=environ)

def delete(url_del, hashing=True, ssl_on=False):

    environ = {}
    if ssl_on:
        environ["wsgi.url_scheme"] = "https"

    if hashing:
        url_del = hmac_hashing(url_del, ssl_on=ssl_on)
    c = Client(app, BaseResponse)
    return c.delete(url_del, environ_overrides=environ)

def test_public_key_nao_encontrado():
    """Tem de retornar 401 para todos os testes, pois não existe a public_key na url"""
    
    assert_code(get(funcionarios), 401)
    assert_code(get(patroes), 401)
    assert_code(get(usuarios), 401)

def test_api_key_nao_encontrado():
    """Tem de retornar 401 para todos os testes, pois não existe a api_key na url"""

    assert_code(get(funcionarios + '?public_key=1', hashing=False), 401)
    assert_code(get(patroes + '?public_key=1', hashing=False), 401)
    assert_code(get(usuarios + '?public_key=1', hashing=False), 401)

def test_timestamp_nao_encontrado():
    """Tem de retornar 401 para todos os testes, pois não existe o timestamp na url"""
    
    assert_code(get(funcionarios + '?public_key=1', hashing=True), 401)
    assert_code(get(patroes + '?public_key=1', hashing=True), 401)
    assert_code(get(usuarios + '?public_key=1', hashing=True), 401) 

def test_public_key_invalido():
    """Tem de retornar 401 para todos os testes, pois a public_key é inválido"""
    
    assert_code(get(funcionarios + '?public_key=20'), 401)
    assert_code(get(patroes + '?public_key=20'), 401)
    assert_code(get(usuarios + '?public_key=20'), 401)

def test_timestamp_invalido():
    """Tem de retornar 401 para todos os testes, pois o timestamp está acima da janela permitida"""
    
    assert_code(get(funcionarios + '?public_key=1&timestamp=' + TIMESTAMP_ANTIGO, hashing=True), 401)
    assert_code(get(patroes + '?public_key=1&timestamp=' + TIMESTAMP_ANTIGO, hashing=True), 401)
    assert_code(get(usuarios + '?public_key=1&timestamp=' + TIMESTAMP_ANTIGO, hashing=True), 401)

def test_GET_valido():
    """Tem de retornar 200 para todos os testes, pois a URL é completamente valida"""
    
    assert_code(get(funcionarios + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True), 200)
    assert_code(get(patroes + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True), 200)
    assert_code(get(usuarios + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True), 200)

def test_GET_valido_SSL():
    """Tem de retornar 200 para todos os testes, pois a URL é completamente valida, usando SSL (HTTPS)"""
    
    assert_code(get(funcionarios + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True, ssl_on=True), 200)
    assert_code(get(patroes + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True, ssl_on=True), 200)
    assert_code(get(usuarios + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, hashing=True, ssl_on=True), 200)

def test_GET_quantidade_correta_patroes():
    """Tem de retornar a quantidade de patroes definida em QTD_PATROES"""

    response = get(patroes + '?public_key=1&timestamp=' + TIMESTAMP_AGORA)
    patroes_json = json.loads(response.data)
    assert len(patroes_json['objects']) == QTD_PATROES

def test_POST_cricao_usuario():
    """Tem de retornar o codigo 201, informando que o usuario foi cadastrado"""
    
    response = post(usuarios + '?public_key=' + settings.SECRET_ID + '&timestamp=' + TIMESTAMP_AGORA, {"password":"123", "username":"matheuscas"})  
    assert_code(response, 201)

def test_PUT_edicao_usuario():
    """Tem de retornar o codigo 204, pois informará que o usuário foi atualizado"""
    
    response = put(usuarios + '1/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, {"first_name":"First Name"}) 
    assert_code(response, 204)

def test_PATCH_edicao_usuario():
    """Tem de retornar o codigo 202, pois informará que a atualização do usuário foi aceita (PATCH)"""
    
    response = patch(usuarios + '1/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, {"first_name":"Patched Name"}) 
    assert_code(response, 202)

def test_DELETE_usuario():
    """Tem de retornar o codigo 204, pois informará que o usuário foi excluído"""
    
    response = delete(usuarios + '1/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA)   
    assert_code(response, 204)

def test_POST_funcionario():
    """Tem de retornar o codigo 201, informando que o funcionario foi cadastrado"""

    response = post(funcionarios + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"nome":"Funcionario", "patrao":"/api/v1/patrao/1/", "usuario":"/api/v1/usuario/2/"})  
    assert_code(response, 201)

def test_POST_funcionario_UTF8():
	"""Tem de retornar o codigo 201, informando que o funcionario, COM ACENTO, foi cadastrado"""

	response = post(funcionarios + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"nome":"Funcionáriõôè @#$%*()_+", "patrao":"/api/v1/patrao/1/", "usuario":"/api/v1/usuario/2/"})	
	assert_code(response, 201)	

def test_PUT_funcionario():
    """Tem de retornar o codigo 204, pois informará que o funcionario foi atualizado"""

    response = put(funcionarios + '1/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"nome":"Funcionario Atualizado"})   
    assert_code(response, 204)

def test_PATCH_funcionario():
    """Tem de retornar o codigo 202, pois informará que a atualização do funcionário foi aceita (PATCH)"""

    response = patch(funcionarios + '1/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"nome":"Funcionario Atualizado"})   
    assert_code(response, 202)

def test_DELETE_funcionario():
    """Tem de retornar o codigo 204, pois informará que o funcionario foi excluído"""

    response = delete(funcionarios + '1/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA)   
    assert_code(response, 204)

def test_POST_patrao():
    """Tem de retornar o codigo 201, informando que o patrao foi cadastrado"""

    response = post(patroes + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"usuario":"/api/v1/usuario/2/"})   
    assert_code(response, 201)

def test_PUT_patrao():
    """Tem de retornar o codigo 204, pois informará que o patrao foi atualizado"""

    response = put(patroes + '2/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"usuario":"/api/v1/usuario/3/"}) 
    assert_code(response, 204)

def test_PATCH_patrao():
    """Tem de retornar o codigo 202, pois informará que a atualização do patrão foi aceita (PATCH)"""

    response = patch(patroes + '2/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA, {"usuario":"/api/v1/usuario/3/"}) 
    assert_code(response, 202)

def test_DELETE_patrao():
    """Tem de retornar o codigo 204, pois informará que o patrao foi excluído"""

    response = delete(patroes + '1/' + '?public_key=2&timestamp=' + TIMESTAMP_AGORA)    
    assert_code(response, 204)

def test_POST_criacao_usuario_SSL():
    """Tem de retornar o codigo 201, informando que o usuario foi cadastrado, usando SSL (HTTPS)"""

    response = post(usuarios + '?public_key=' + settings.SECRET_ID + '&timestamp=' + TIMESTAMP_AGORA, {"password":"123", "username":"matheuscassl"}, ssl_on=True)  
    assert_code(response, 201)

def test_PUT_edicao_usuario_SSL():
    """Tem de retornar o codigo 204, pois informará que o usuário foi atualizado, usando SSL (HTTPS)"""

    response = put(usuarios + '2/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, {"first_name":"First Name SSL"}, ssl_on=True)
    assert_code(response, 204)

def test_PATCH_edicao_usuario_SSL():
    """Tem de retornar o codigo 202, pois informará que a atualização do usuário foi aceita (PATCH), usando SSL (HTTPS)"""

    response = patch(usuarios + '2/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, {"first_name":"Patched Name SSL"}, ssl_on=True)
    assert_code(response, 202)

def test_DELETE_usuario_SSL():
    """Tem de retornar o codigo 204, pois informará que o usuário foi excluído, usando SSL (HTTPS)"""

    response = delete(usuarios + '2/' + '?public_key=1&timestamp=' + TIMESTAMP_AGORA, ssl_on=True)
    assert_code(response, 204)
