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

from horizon.test.settings import *  # noqa
from openstack_dashboard.test.settings import *  # noqa
import openstack_dashboard.enabled
from openstack_dashboard.utils import settings

import neutron_taas_dashboard.enabled

HORIZON_CONFIG.pop('dashboards', None)
HORIZON_CONFIG.pop('default_dashboard', None)

settings.update_dashboards(
    [
        openstack_dashboard.enabled,
        neutron_taas_dashboard.enabled,
    ],
    HORIZON_CONFIG,
    INSTALLED_APPS
)

INSTALLED_APPS = list(set(INSTALLED_APPS))

TEST_GLOBAL_MOCKS_ON_PANELS['tap_mirrors'] = {
    'method': ('neutron_taas_dashboard.dashboards.project.tap_mirrors.panel.'
               'TapMirrors.can_access'),
    'return_value': True,
}
