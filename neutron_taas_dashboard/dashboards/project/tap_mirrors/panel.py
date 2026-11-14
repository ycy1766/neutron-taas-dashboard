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

from django.utils.translation import gettext_lazy as _
import horizon

from neutron_taas_dashboard.api import taas as api_taas

LOG = logging.getLogger(__name__)


class TapMirrors(horizon.Panel):
    name = _("Tap Mirrors")
    slug = 'tap_mirrors'
    permissions = ('openstack.services.network',)
    # Checked by horizon.Panel._can_access when POLICY_CHECK_FUNCTION is set.
    policy_rules = (("network", "get_tap_mirror"),)

    def allowed(self, context):
        request = context['request']
        if not request.user.has_perms(self.permissions):
            return False
        if not api_taas.is_supported(request):
            return False
        return super().allowed(context)
