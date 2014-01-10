# -*- coding: utf-8 -*-

import warnings

from django.template import RequestContext
from django.template.loader import render_to_string

from openslides.config.api import config
from openslides.utils.exceptions import OpenSlidesError

from .exceptions import ProjectorExceptionWarning


class Widget(object):
    """
    Class for a Widget for the Projector-Tab.
    """
    def __init__(self, request, name, html=None, template=None, context=None,
                 permission_required=None, display_name=None, default_column=1,
                 default_weight=0):
        self.name = name
        if display_name is None:
            self.display_name = name.capitalize()
        else:
            self.display_name = display_name

        if html is not None:
            self.html = html
        elif template is not None:
            self.html = render_to_string(
                template_name=template,
                dictionary=context or {},
                context_instance=RequestContext(request))
        else:
            raise OpenSlidesError('A Widget must have either a html or a template argument.')
        self.permission_required = permission_required
        self.default_column = default_column
        self.default_weight = default_weight

    def get_name(self):
        """
        Returns the lower case of the widget name.
        """
        return self.name.lower()

    def get_html(self):
        """
        Returns the html code of the widget.
        """
        return self.html

    def get_title(self):
        """
        Returns the title of the widget.
        """
        return self.display_name

    def __repr__(self):
        return repr(self.display_name)

    def __unicode__(self):
        return unicode(self.display_name)


class Overlay(object):
    """
    Represents an overlay which can be seen on the projector.
    """

    def __init__(self, name, get_widget_html, get_projector_html,
                 get_javascript=None, allways_active=False):
        self.name = name
        self.widget_html_callback = get_widget_html
        self.projector_html_callback = get_projector_html
        self.javascript_callback = get_javascript
        self.allways_active = allways_active

    def __repr__(self):
        return self.name

    def get_widget_html(self):
        """
        Returns the html code for the overlay widget.

        Can return None, if the widget does not want to be in the widget.
        """
        value = None
        if self.widget_html_callback is not None:
            value = self.widget_html_callback()
        return value

    def get_projector_html(self):
        """
        Returns the html code for the projector.
        """
        try:
            value = self.get_html_wrapper(self.projector_html_callback())
        except Exception as exception:
            warnings.warn('%s in overlay "%s": %s'
                          % (type(exception).__name__, self, exception),
                          ProjectorExceptionWarning)
            value = ''
        return value

    def get_javascript(self):
        """
        Returns the java-script code for the projector.
        """
        if self.javascript_callback is None:
            value = {}
        else:
            value = self.javascript_callback()
        return value

    def get_html_wrapper(self, inner_html):
        """
        Returns the inner_html wrapped in a div.

        The html-id of the div is "overlay_OVERLAYNAME"
        """
        full_html = ''
        if inner_html is not None:
            full_html = '<div id="overlay_%s">%s</div>' % (self.name, inner_html)
        return full_html

    def is_active(self):
        """
        Returns True if the overlay is activated. False in other case.
        """
        return self.allways_active or self.name in config['projector_active_overlays']

    def set_active(self, active):
        """
        Publish or depublish the overlay on the projector.

        publish, if active is true,
        depublish, if active is false.
        """
        active_overlays = set(config['projector_active_overlays'])
        if active:
            active_overlays.add(self.name)
        else:
            active_overlays.discard(self.name)
        config['projector_active_overlays'] = list(active_overlays)

    def show_on_projector(self):
        """
        Retruns True if the overlay should be shoun on the projector.
        """
        return self.is_active() and self.get_projector_html() is not None
