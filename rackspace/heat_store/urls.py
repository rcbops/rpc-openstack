try:
    from django.conf.urls.defaults import patterns, url
except ImportError:  # Django 1.6
    from django.conf.urls import patterns, url

from rackspace.heat_store.views import IndexView, MoreInformationView

urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index'),
                       url(r'^more_info/(?P<template_id>.+)$',
                           MoreInformationView.as_view(),
                           name='more_info'),
                       )
