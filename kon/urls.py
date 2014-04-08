from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from game.views import SignUpView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kamal1.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'game.views.home', name='home'),
    url(r'^signup/$', SignUpView.as_view(), name='signup'),
    url(r'^game/(?P<pk>\d+)/$', 'game.views.game_detail', name='game_detail'),
    url(r'^invite/$', 'game.views.new_invitation', name='invite'),
    url(r'^invitation/(?P<pk>\d+)/$', 'game.views.accept_invitation', name='accept_invitation'),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout$', 'logout', {'next_page': '/'}, name='logout'),
)