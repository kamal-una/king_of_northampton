from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kamal1.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'app1.views.home', name='home'),
    url(r'^game/(?P<pk>\d+)/$', 'app1.views.game_detail', name='game_detail'),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'logout', {'next_page': 'home'}, name='logout'),
)