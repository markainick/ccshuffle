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
from django.views import generic
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import redirect, render_to_response
from ccshuffle.serialize import ResponseObject, JSONModelEncoder
from .models import CrawlingProcess
from .crawler import JamendoCrawler

logger = logging.getLogger(__name__)


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
                    response_object = ResponseObject(result_obj=JamendoCrawler.crawl())
                    return HttpResponse(response_object.json(cls=JSONModelEncoder))
                except BaseException as e:
                    response_object = ResponseObject(status='fail', error_msg=str(e))
                    return HttpResponse(response_object.json(), status=500)
            else:
                response_object = ResponseObject(status='fail', error_msg='The given command is unknown !')
                return HttpResponse(response_object.json(), status=400)
        else:
            response_object = ResponseObject(status='fail', error_msg='No command is given !')
            return HttpResponse(response_object.json(), status=400)
