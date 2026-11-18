# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django import shortcuts
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import messages
from horizon import tables as horizon_tables
from horizon import tabs as horizon_tabs
from horizon.utils import memoized
from openstack_dashboard import policy

from neutron_taas_dashboard.api import taas as api_taas
from neutron_taas_dashboard.dashboards.project.tap_mirrors import forms
from neutron_taas_dashboard.dashboards.project.tap_mirrors import tables
from neutron_taas_dashboard.dashboards.project.tap_mirrors import tabs


class IndexView(horizon_tables.DataTableView):
    table_class = tables.TapMirrorsTable
    template_name = 'project/tap_mirrors/index.html'
    page_title = _("Tap Mirrors")

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            tap_mirrors = api_taas.tap_mirror_list(
                self.request, project_id=tenant_id,
                mirror_type=api_taas.MIRROR_TYPE_LPORT)
        except Exception:
            tap_mirrors = []
            exceptions.handle(self.request,
                              _('Unable to retrieve tap mirrors.'))
        return api_taas.annotate_ports(self.request, tap_mirrors)


class CreateView(horizon_forms.ModalFormView):
    form_class = forms.CreateTapMirror
    form_id = "create_tap_mirror_form"
    template_name = 'project/tap_mirrors/create.html'
    submit_label = _("Create Tap Mirror")
    submit_url = reverse_lazy("horizon:project:tap_mirrors:create")
    success_url = reverse_lazy("horizon:project:tap_mirrors:index")
    page_title = _("Create Tap Mirror")
    policy_rules = (("network", "create_tap_mirror"),)

    def dispatch(self, request, *args, **kwargs):
        # The table only hides the button; check the same rule here so a
        # direct GET/POST of this URL is refused with a message as well.
        # The Neutron policy on the server remains the authority.
        if not policy.check(self.policy_rules, request):
            messages.error(request,
                           _('You are not allowed to create tap mirrors.'))
            return shortcuts.redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)


class DetailView(horizon_tabs.TabView):
    tab_group_class = tabs.TapMirrorDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ tap_mirror.name_or_id }}"

    @memoized.memoized_method
    def get_data(self):
        tap_mirror_id = self.kwargs['tap_mirror_id']
        try:
            tap_mirror = api_taas.tap_mirror_get(self.request, tap_mirror_id)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve tap mirror details.'),
                              redirect=self.get_redirect_url())
        api_taas.annotate_ports(self.request, [tap_mirror])
        return tap_mirror

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tap_mirror = self.get_data()
        table = tables.TapMirrorsTable(self.request)
        context["tap_mirror"] = tap_mirror
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(tap_mirror)
        return context

    def get_tabs(self, request, *args, **kwargs):
        tap_mirror = self.get_data()
        return self.tab_group_class(request, tap_mirror=tap_mirror, **kwargs)

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:project:tap_mirrors:index')
