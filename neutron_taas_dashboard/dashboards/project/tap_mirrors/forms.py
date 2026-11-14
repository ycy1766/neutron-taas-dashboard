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

import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from neutron_taas_dashboard.api import taas as api_taas

LOG = logging.getLogger(__name__)


class CreateTapMirror(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"), required=False)
    description = forms.CharField(
        max_length=255, label=_("Description"), required=False,
        widget=forms.Textarea(attrs={'rows': 2}))
    port_id = forms.ThemableChoiceField(
        label=_("Source Port"),
        help_text=_("The VM port whose traffic is copied."))
    remote_port_id = forms.ThemableChoiceField(
        label=_("Collector Port"),
        help_text=_("The VM port that receives the copy. It must belong to "
                    "this project and must not be the source port."))
    direction = forms.ThemableChoiceField(
        label=_("Direction"),
        choices=api_taas.DIRECTION_CHOICES,
        initial=api_taas.DIRECTION_BOTH,
        help_text=_("Egress is copied before, ingress after the security "
                    "groups of the source port are applied."))

    failure_url = 'horizon:project:tap_mirrors:index'

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        try:
            choices = api_taas.mirrorable_port_choices(request)
        except Exception:
            choices = []
            exceptions.handle(request, _('Unable to retrieve ports.'))
        if not choices:
            choices = [('', _("No VM ports available"))]
        self.fields['port_id'].choices = choices
        self.fields['remote_port_id'].choices = choices

    def clean(self):
        cleaned = super().clean()
        if (cleaned.get('port_id') and
                cleaned.get('port_id') == cleaned.get('remote_port_id')):
            raise forms.ValidationError(
                _("The source port and the collector port must differ."))
        return cleaned

    def handle(self, request, data):
        try:
            tap_mirror = api_taas.lport_mirror_create(
                request,
                name=data['name'],
                description=data['description'],
                port_id=data['port_id'],
                remote_port_id=data['remote_port_id'],
                direction=data['direction'])
            msg = _('Tap mirror %s was successfully created.') % (
                tap_mirror.name_or_id)
            messages.success(request, msg)
            return tap_mirror
        except Exception as e:
            LOG.info('Failed to create tap mirror: %s', e)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, _('Unable to create tap mirror.'),
                              redirect=redirect)
