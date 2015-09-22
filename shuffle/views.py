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

import logging

from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponse

from ccshuffle.serialize import ResponseObject
from .forms import LoginForm, RegistrationForm
from .searchengine import SearchEngine

logger = logging.getLogger(__name__)


class IndexPageView(generic.TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        request.session['last_url'] = request.get_full_path()
        kwargs['tags'] = SearchEngine.all_tags()
        search_for = request.GET.get('search_for', None)
        if search_for:
            search_request = SearchEngine.SearchRequest(search_phrase=request.GET.get('search_phrase', ''),
                                                        search_for=search_for)
            search_response = SearchEngine.accept(search_request)
            search_result_offset = int(request.GET.get('start', 0))
            kwargs['search_result_count'] = len(search_response.search_result)
            kwargs['search_offset'] = search_result_offset
            kwargs['search_result'] = list(
                search_response.search_result[search_result_offset:search_result_offset + 10])
            if search_for == 'songs':
                kwargs['searched_tags'] = search_response.extracted_tags
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

    @classmethod
    def is_username_available(cls, request):
        print(request.method)
        if request.is_ajax() and request.method == 'GET':
            username = request.GET.get('username', None)
            if username:
                return HttpResponse(
                    ResponseObject('success', 'Fails', not User.objects.filter(username=username).exists()).json(),
                    content_type="json")
            else:
                return HttpResponse(ResponseObject('fail', 'The username to check must be given.', None).json(),
                                    content_type="json")
        else:
            return redirect('404')


class NotFoundErrorPageView(generic.TemplateView):
    """
    This class represents an error page, which will be displayed, if the page (the user looked for) can't be found on
    the server.
    """
    template_name = '404.html'

    def get(self, request, *args, **kwargs):
        logger.info("Get (Not found) %s" % request.session['last_url'])
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)

    def get_context_data(self, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['globalLoginForm'] = LoginForm
        return context
