from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import datetime
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from models import Funcionario


def lista(request):
    lista = Funcionario.objects.filter(patrao=request.user)
    return render_to_response(
        'rh/lista.html',
        locals(),
        context_instance=RequestContext(request),
        )


def individual(request, funcionario_id):
    elemento = get_object_or_404(Funcionario, id=funcionario_id)
    return render_to_response(
        'rh/individual.html',
        locals(),
        context_instance=RequestContext(request),
        )

