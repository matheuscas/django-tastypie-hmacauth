from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
import hashlib
from datetime import datetime

SITUACAO = (('S','Ativo'),('N','Inativo'))


class Patrao(models.Model):
    class Meta:
        db_table = "Patrao"
        verbose_name = u'Patrao' 
        verbose_name_plural = u'Patrao'        
        ordering = ('data_de_cadastro',)  
    usuario = models.ForeignKey(User)

    data_de_cadastro = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de cadastro no Sistema", auto_now_add=True)
    data_de_atualizacao = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de atualizacao no Sistema", auto_now=True)
    def __unicode__(self):
        return u'%s' % (self.usuario.username)

    def get_absolute_url(self):
        return '%d'%self.id

class Funcionario(models.Model):
    class Meta:
        db_table = "Funcionario"
        verbose_name = u'Funcionario' 
        verbose_name_plural = u'Funcionarios'        
        ordering = ('data_de_cadastro',) 
    patrao = models.ForeignKey('Patrao') 
    usuario = models.ForeignKey(User)
    nome = models.CharField(max_length=100,blank=True)
    foto = models.FileField(
        null=True,
        blank=True,
        upload_to='uploads/rh/img/',
        )
    rg = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)  
    cpf = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)  
    data_de_nascimento = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de cadastro no Sistema", auto_now_add=True)
    telefone_residencial = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2) 
    telefone_celular = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2) 
    telefone_residencial = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2) 
    email = models.EmailField(max_length=70,blank=True)
    cargo = models.CharField(max_length=100,blank=True)
    data_de_admissao = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de admissao do funcionario", auto_now_add=True)
  
    data_de_cadastro = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de cadastro no Sistema", auto_now_add=True)
    data_de_atualizacao = models.DateTimeField(default=datetime.now, blank=True, null=True, verbose_name="data de atualizacao no Sistema", auto_now=True)
    def __unicode__(self):
        return u'%s' % (self.nome)

    def get_absolute_url(self):
        return '%d'%self.id
