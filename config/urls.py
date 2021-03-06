# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.core.cache import cache
from django.db.utils import ProgrammingError
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.conf.urls.static import static

from sitetree.sitetreeapp import register_dynamic_trees, compose_dynamic_tree
from sitetree.sitetreeapp import register_i18n_trees
from sitetree import sitetreeapp

from velo.core.sitetrees import sitetrees_build
from velo.core.views import CalendarView, IndexView
from velo.marketing.views import ToyotaFrameView
from velo.payment.views import ApplicationPayView, ApplicationOKView, TransactionReturnView, InvoiceDownloadView, \
    DiscountCheckView
from velo.registration.views import ApplicationUpdate, ApplicationCreate, CompanyApplicationCreate, CompanyApplicationDetail, \
    CompanyApplicationParticipantAdd, MyCompanyApplicationList, CompanyApplicationParticipantAddOK, \
    CompanyApplicationUpdate, ParticipantPDF
from velo.results.views import ResultAllView
from velo.staticpage.views import StaticPageView, SimpleStaticPageView
from velo.velo.views import CustomAutoResponseView, cached_javascript_catalog

admin.autodiscover()

def register_sitetrees():
    sitetreeapp._DYNAMIC_TREES.clear()
    cache.delete('sitetrees')
    register_i18n_trees(['mainmenu', 'competition_admin', 'footermenu'])
    try:
        register_dynamic_trees((
            compose_dynamic_tree(sitetrees_build('lv'), target_tree_alias='mainmenu_lv', parent_tree_item_alias='sacensibas'),
            compose_dynamic_tree(sitetrees_build('en'), target_tree_alias='mainmenu_en', parent_tree_item_alias='sacensibas'),
            compose_dynamic_tree(sitetrees_build('ru'), target_tree_alias='mainmenu_ru', parent_tree_item_alias='sacensibas'),
            compose_dynamic_tree('velo.manager', target_tree_alias='mainmenu_lv', parent_tree_item_alias='manager'),
        ), reset_cache=True)
    except ProgrammingError:
        print('Seems that migrations should be run.')
register_sitetrees()


js_info_dict = {
    # Not yet used
}

urlpatterns = i18n_patterns(
    url(r'^$', IndexView.as_view(), name='index'),

    url(_(r'^application/$'), ApplicationCreate.as_view(), name='application'),
    url(_(r'^application/(?P<pick>\d+)/$'), ApplicationCreate.as_view(), name='application'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'), ApplicationUpdate.as_view(), name='application'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/pay/$'), ApplicationPayView.as_view(), name='application_pay'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/ok/$'), ApplicationOKView.as_view(), name='application_ok'),
    url(_(r'^application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/discount/$'), DiscountCheckView.as_view(), name='check_discount'),



    url(_(r'^company_application/$'), MyCompanyApplicationList.as_view(), name='companyapplication_list'),
    url(_(r'^company_application/add/$'), CompanyApplicationCreate.as_view(), name='companyapplication'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'), CompanyApplicationDetail.as_view(), name='companyapplication'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/add/$'), CompanyApplicationParticipantAdd.as_view(), name='companyapplication_add'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/ok/$'), CompanyApplicationParticipantAddOK.as_view(), name='companyapplication_ok'),
    url(_(r'^company_application/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/edit/$'), CompanyApplicationUpdate.as_view(), name='companyapplication_edit'),


    url(_(r'^results/'), ResultAllView.as_view(), name="all_results"),
    url(_(r'^payment/'), include('velo.payment.urls', namespace='payment')),
    url(_(r'^whatever/'), include('velo.advert.urls', namespace='advert')),
    url(_(r'^news/'), include('velo.news.urls', namespace='news')),
    url(_(r'^gallery/'), include('velo.gallery.urls', namespace='gallery')),
    url(_(r'^mk/'), include('velo.marketing.urls', namespace='marketing')),
    url(r'^manager/', include('velo.manager.urls', namespace='manager')),
    url(_(r'^competition/'), include('velo.velo.urls_competition', namespace='competition')),
    url(_(r'^calendar/'), CalendarView.as_view(), name="calendar"),
    url(_(r'^account/'), include('velo.core.urls', namespace='account')),
    url(_(r'^account/'), include('allauth.urls')),
    url(r'^jsi18n/$', cached_javascript_catalog, js_info_dict),

    url(r'^toyota/$', ToyotaFrameView.as_view(), name='marketing_toyota'),
    url(r'(?P<slug>.*)/$', SimpleStaticPageView.as_view(), name='simple_staticpage'),
)


urlpatterns += [
    url(r'^$', RedirectView.as_view(url='/lv/')),
    url(_(r'^bank/return/$'), TransactionReturnView.as_view(), name='payment_bank_return'),
    url(r'^payment/invoice/(?P<slug>.+)/$', InvoiceDownloadView.as_view(), name='invoice_pdf'),

    # url('^s/', include('shorturls.urls')),
    url(_(r'^pdf/(?P<slug>\w+)/'), ParticipantPDF.as_view(), name="participant_number_pdf"),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^%s' % settings.ADMIN_URL, include(admin.site.urls)),  # This is real admin with hidden link in ENV

    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r"^json/fields/auto.json$", CustomAutoResponseView.as_view(), name="django_select2-json"),
    url(r'^markdownx/', include('markdownx.urls')),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    if 'rosetta' in settings.INSTALLED_APPS:
        urlpatterns += [
            url(r'^rosetta/', include('rosetta.urls')),
        ]
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
