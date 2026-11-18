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

"""All Neutron (TaaS) calls of the plugin.

This is the only module that talks to Neutron. Horizon up to 2025.1 builds
a ``python-neutronclient`` client (``api.neutron.neutronclient``); later
releases only have the openstacksdk based ``api.neutron.networkclient``.
Both are supported: the neutronclient path uses the generic HTTP methods,
the SDK path the ``tap_mirror`` proxy methods of openstacksdk >= 4.4.
"""

import logging

from django.utils.translation import gettext_lazy as _
from openstack_dashboard.api import neutron
from openstack_dashboard.api import nova

LOG = logging.getLogger(__name__)

# Neutron extension that adds the ``lport`` mirror type.
EXTENSION_ALIAS = 'tap-mirror-lport'
# ``OPENSTACK_NEUTRON_NETWORK`` key that can hide the panel.
CONFIG_NAME = 'enable_taas'

MIRROR_TYPE_LPORT = 'lport'

TAP_MIRRORS_PATH = '/taas/tap_mirrors'
TAP_MIRROR_PATH = TAP_MIRRORS_PATH + '/%s'
# Query parameters the openstacksdk TapMirror resource accepts; the other
# filters are applied locally on the SDK path.
SDK_QUERY_PARAMS = ('name', 'project_id', 'sort_key', 'sort_dir')

# Keys of the ``directions`` attribute. For an ``lport`` mirror the values
# (tunnel ids) are always null; only the keys select the directions.
DIRECTION_IN = 'IN'
DIRECTION_OUT = 'OUT'
DIRECTION_BOTH = 'BOTH'

DIRECTION_CHOICES = (
    (DIRECTION_BOTH, _("Both directions")),
    (DIRECTION_IN, _("Ingress (traffic going to the source port)")),
    (DIRECTION_OUT, _("Egress (traffic leaving the source port)")),
)
DIRECTION_LABELS = dict(DIRECTION_CHOICES)

# First version: only VM ports are offered. This is a UI restriction, the
# server accepts any bound port of the project.
MIRRORABLE_DEVICE_OWNER_PREFIX = 'compute:'


class TapMirror(neutron.NeutronAPIDictWrapper):
    """Wrapper for a ``tap_mirror`` resource."""

    @property
    def direction(self):
        keys = set((self._apidict.get('directions') or {}).keys())
        if DIRECTION_BOTH in keys or {DIRECTION_IN, DIRECTION_OUT} <= keys:
            return DIRECTION_BOTH
        if keys:
            return sorted(keys)[0]
        return None

    @property
    def direction_display(self):
        direction = self.direction
        return DIRECTION_LABELS.get(direction, direction or '-')


def is_supported(request):
    """True when the panel can be shown for this request.

    This only checks the extension advertisement and the dashboard setting.
    It says nothing about what the user is allowed to do: that is decided
    by the Neutron policy when a call is made.
    """
    try:
        return neutron.is_service_enabled(request,
                                          config_name=CONFIG_NAME,
                                          ext_name=EXTENSION_ALIAS)
    except Exception:
        LOG.exception("Unable to list Neutron extensions; the Tap Mirrors "
                      "panel will not be displayed.")
        return False


def _use_neutronclient():
    """True on Horizon releases that still build python-neutronclient."""
    return hasattr(neutron, 'neutronclient')


def tap_mirror_list(request, **params):
    if _use_neutronclient():
        client = neutron.neutronclient(request)
        body = client.list_ext('tap_mirrors', TAP_MIRRORS_PATH,
                               retrieve_all=True, **params)
        return [TapMirror(m) for m in body.get('tap_mirrors', [])]
    query = {k: v for k, v in params.items() if k in SDK_QUERY_PARAMS}
    local = {k: v for k, v in params.items() if k not in SDK_QUERY_PARAMS}
    mirrors = [TapMirror(m.to_dict())
               for m in neutron.networkclient(request).tap_mirrors(**query)]
    return [m for m in mirrors
            if all(m._apidict.get(k) == v for k, v in local.items())]


def tap_mirror_get(request, tap_mirror_id):
    if _use_neutronclient():
        client = neutron.neutronclient(request)
        body = client.show_ext(TAP_MIRROR_PATH, tap_mirror_id)
        return TapMirror(body['tap_mirror'])
    mirror = neutron.networkclient(request).get_tap_mirror(tap_mirror_id)
    return TapMirror(mirror.to_dict())


def tap_mirror_create(request, **attrs):
    if _use_neutronclient():
        client = neutron.neutronclient(request)
        body = client.create_ext(TAP_MIRRORS_PATH, {'tap_mirror': attrs})
        return TapMirror(body['tap_mirror'])
    mirror = neutron.networkclient(request).create_tap_mirror(**attrs)
    return TapMirror(mirror.to_dict())


def tap_mirror_delete(request, tap_mirror_id):
    if _use_neutronclient():
        client = neutron.neutronclient(request)
        client.delete_ext(TAP_MIRROR_PATH, tap_mirror_id)
        return
    neutron.networkclient(request).delete_tap_mirror(tap_mirror_id,
                                                     ignore_missing=False)


def lport_mirror_create(request, name, description, port_id,
                        remote_port_id, direction):
    """Create an ``lport`` mirror from the form values."""
    return tap_mirror_create(request,
                             name=name,
                             description=description,
                             mirror_type=MIRROR_TYPE_LPORT,
                             port_id=port_id,
                             remote_port_id=remote_port_id,
                             directions={direction: None})


def _server_names(request):
    # Without the ``paginate`` option Horizon asks Nova for one unlimited
    # list, but Nova still caps it at its ``osapi_max_limit`` (1000 by
    # default). In a project with more servers than that, the ports of the
    # remaining servers are labelled with the device id instead of the name.
    try:
        servers, _more = nova.server_list(request)
    except Exception:
        LOG.exception("Unable to list servers; ports are shown by id.")
        return {}
    return {s.id: s.name for s in servers}


def _network_names(request):
    tenant_id = request.user.tenant_id
    try:
        networks = neutron.network_list_for_tenant(request, tenant_id)
    except Exception:
        LOG.exception("Unable to list networks; ports are shown by id.")
        return {}
    return {n.id: n.name_or_id for n in networks}


def port_label(port, server_names=None, network_names=None):
    """Human readable label of a port for choices and tables.

    ``<server> | <network> | <ip, ip> | <port name or short id>``
    """
    server_names = server_names or {}
    network_names = network_names or {}
    device = server_names.get(port.device_id, port.device_id or '-')
    network = network_names.get(port.network_id, port.network_id or '-')
    ips = ', '.join(ip.get('ip_address', '') for ip in port.fixed_ips or [])
    name = port.name or port.id[:8]
    return '%s | %s | %s | %s' % (device, network, ips or '-', name)


def project_ports(request):
    """All ports of the project as ``{id: label}``."""
    tenant_id = request.user.tenant_id
    ports = neutron.port_list(request, tenant_id=tenant_id)
    server_names = _server_names(request)
    network_names = _network_names(request)
    return {p.id: port_label(p, server_names, network_names)
            for p in ports}


def mirrorable_port_choices(request):
    """``(id, label)`` choices of the VM ports of the project."""
    tenant_id = request.user.tenant_id
    ports = [p for p in neutron.port_list(request, tenant_id=tenant_id)
             if (p.device_owner or '').startswith(
                 MIRRORABLE_DEVICE_OWNER_PREFIX)]
    server_names = _server_names(request)
    network_names = _network_names(request)
    choices = [(p.id, port_label(p, server_names, network_names))
               for p in ports]
    return sorted(choices, key=lambda c: c[1])


def annotate_ports(request, tap_mirrors):
    """Attach ``port_display`` / ``remote_port_display`` to the wrappers."""
    if not tap_mirrors:
        return tap_mirrors
    try:
        labels = project_ports(request)
    except Exception:
        LOG.exception("Unable to list ports; tap mirror ports are shown "
                      "by id.")
        labels = {}
    for tm in tap_mirrors:
        tm.port_display = labels.get(tm.port_id, tm.port_id)
        tm.remote_port_display = labels.get(tm.remote_port_id,
                                            tm.remote_port_id or '-')
    return tap_mirrors
