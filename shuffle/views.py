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

import logging

logger = logging.getLogger(__name__)


class IndexPageView(generic.TemplateView):
    template_name = 'base.html'

    def get(self, request, *args, **kwargs):
        request.session['last_url'] = request.get_full_path()
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

        :param request:
        :return:
        """
        logger.debug('%s: Ajax request' % self.__class__.__name__)
        logger.debug('%s' % request.GET)
        ajax_data = request.GET
        if 'command' in ajax_data:
            if ajax_data['command'] == 'start-jamendo-crawl':
                try:
                    jamendo_engine = JamendoSearchEngine()
                    return HttpResponse(jamendo_engine.crawl(), status=200)
                except BaseException as e:
                    return HttpResponse('During the crawling an error occurred (%s)' % e, status=500)
            else:
                return HttpResponse('The given command is unknown !', status=400)
        else:
            return HttpResponse('No command is given !', status=400)
