#   COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from .forms import LoginForm, RegistrationForm
from .searchengine import JamendoSearchEngine
from .models import JSONModelEncoder, CrawlingProcess, Song

import logging
import json

logger = logging.getLogger(__name__)


class ResponseObject(object):
    """ Response object for the ajax requests of the dashboard """

    def __init__(self, status='success', error_msg='', result_obj=None):
        """
        Initializes the response object.

        :param status: success or fail.
        :param error_msg: the error message if the status is 'fail'.
        :param result_obj: the result object, which is json serializable.
        """
        self.response_dic = {
            'header': {'status': status, 'error_message': error_msg},
            'result': result_obj,
        }

    def result_object(self):
        """
        Returns the the same object passed through the constructor as result object.

        :return: the same object passed through the constructor.
        """
        return self.response_dic['result']

    def json(self, cls=None):
        """
        Returns the json dump of the result object.

        :param cls: optional the class for serializing the result object, otherwise the default serializer
                    JSONEncoder.
        :return: the json dump of the result object.
        """
        return json.dumps(self.response_dic, cls=cls)


class IndexPageView(generic.TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        request.session['last_url'] = request.get_full_path()
        if request.GET.get('search_for', None):
            kwargs['search_result'] = list(Song.objects.all()[:20])
            if 'tags' == request.GET.get('search_for'):
                kwargs['searched_tags'] = request.GET.get('search_phrase', '').split(' ')
        return super(IndexPageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['globalLoginForm'] = LoginForm
        return context


class AboutPageView(generic.TemplateView):
    """
    This class represents the view of the about page. This page contains information about the creative commons
    shuffle service.
    """
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['globalLoginForm'] = LoginForm
        return context


class SignInPageView(generic.FormView):
    form_class = LoginForm
    success_url = reverse_lazy('home')
    template_name = 'signin.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        logger.info(username + " logged in.")
        if user is not None and user.is_active:
            login(self.request, user)
            return super(SignInPageView, self).form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        form.cleaned_data['next'] = self.success_url
        return super(SignInPageView, self).form_invalid(form)

    def post(self, request, *args, **kwargs):
        self.success_url = request.POST.get('next', request.GET.get('next', reverse_lazy('home')))
        if self.success_url is None or len(self.success_url) == 0:
            self.success_url = reverse_lazy('home')
        return super(SignInPageView, self).post(request, *args, **kwargs)


class SignOutPageView(generic.RedirectView):
    """ The global sign out link. """
    default_redirect_url = reverse_lazy('home')
    url = default_redirect_url

    def get(self, request, *args, **kwargs):
        self.url = request.POST.get('next', request.GET.get('next', reverse_lazy('home')))
        logger.debug("Current Url: %s " % self.url)
        logger.info("Logout. (Redirected to %s)" % self.url)
        logout(request)
        return super(SignOutPageView, self).get(request, *args, **kwargs)


class RegisterPageView(generic.CreateView):
    form_class = RegistrationForm
    model = User
    template_name = 'register.html'
    success_url = reverse_lazy('signin')

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['globalLoginForm'] = LoginForm
        return context


class NotFoundErrorPageView(generic.TemplateView):
    """
    This class represents an error page, which will be displayed, if the page (the user looked for) can't be found on
    the server.
    """
    template_name = '404.html'

    def get(self, request, *args, **kwargs):
        logger.info("Get (Not found) %s" % request.session['last_url'])
        return super(NotFoundErrorPageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['globalLoginForm'] = LoginForm
        return context


class CrawlerPageView(generic.TemplateView):
    """ This class represents the page view for starting the crawling process as well as showing the process. """
    template_name = 'crawler.html'

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['jamendo_cp_list'] = CrawlingProcess.objects.filter(service=CrawlingProcess.Service_Jamendo)
        context['soundcloud_cp_list'] = CrawlingProcess.objects.filter(service=CrawlingProcess.Service_Soundcloud)
        context['ccmixter_cp_list'] = CrawlingProcess.objects.filter(service=CrawlingProcess.Service_CCMixter)
        context['general_cp_list'] = CrawlingProcess.objects.filter(service=CrawlingProcess.Service_General)
        return context

    def get(self, request, *args, **kwargs):
        if request.user is None or not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse_lazy('signin'), request.path))
        else:
            if request.user.is_superuser:
                if request.is_ajax():
                    return self.handle_ajax_request(request)
                else:
                    return super(CrawlerPageView, self).get(request, *args, **kwargs)
            else:
                return render_to_response('403.html', context_instance=RequestContext(request))

    def handle_ajax_request(self, request):
        """
        Handle ajax requests.

        :param request: the request object.
        :return: the http response to the ajax requests.
        """
        logger.debug('%s: Ajax request' % self.__class__.__name__)
        logger.debug('%s' % request.GET)
        ajax_data = request.GET
        if 'command' in ajax_data:
            if ajax_data['command'] == 'start-jamendo-crawl':
                try:
                    response_object = ResponseObject(result_obj=JamendoSearchEngine().crawl())
                    return HttpResponse(response_object.json(cls=JSONModelEncoder))
                except BaseException as e:
                    print(str(e))
                    response_object = ResponseObject(status='fail', error_msg=str(e))
                    return HttpResponse(response_object.json(), status=500)
            else:
                response_object = ResponseObject(status='fail', error_msg='The given command is unknown !')
                return HttpResponse(response_object.json(), status=400)
        else:
            response_object = ResponseObject(status='fail', error_msg='No command is given !')
            return HttpResponse(response_object.json(), status=400)
