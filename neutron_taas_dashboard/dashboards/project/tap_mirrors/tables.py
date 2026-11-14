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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from horizon import tables
from openstack_dashboard import policy

from neutron_taas_dashboard.api import taas as api_taas


class CreateTapMirror(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Tap Mirror")
    url = "horizon:project:tap_mirrors:create"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("network", "create_tap_mirror"),)


class DeleteTapMirror(policy.PolicyTargetMixin, tables.DeleteAction):
    name = "delete"
    policy_rules = (("network", "delete_tap_mirror"),)
    policy_target_attrs = (("project_id", "project_id"),)

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            "Delete Tap Mirror",
            "Delete Tap Mirrors",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            "Deleted Tap Mirror",
            "Deleted Tap Mirrors",
            count
        )

    def allowed(self, request, datum=None):
        # Only ``lport`` mirrors are managed here (see IndexView).
        if (datum is not None and
                datum.mirror_type != api_taas.MIRROR_TYPE_LPORT):
            return False
        return super().allowed(request, datum)

    def delete(self, request, obj_id):
        # Let errors propagate: BatchAction counts the row as failed and
        # shows one aggregated error message. Handling the exception here
        # and returning normally would report the deletion as a success.
        api_taas.tap_mirror_delete(request, obj_id)


def _port_url(port_id):
    if not port_id:
        return None
    return reverse('horizon:project:networks:ports:detail', args=[port_id])


class TapMirrorsTable(tables.DataTable):
    name = tables.WrappingColumn(
        "name_or_id",
        verbose_name=_("Name"),
        link="horizon:project:tap_mirrors:detail")
    port = tables.Column(
        "port_display",
        verbose_name=_("Source Port"),
        link=lambda tm: _port_url(tm.port_id))
    remote_port = tables.Column(
        "remote_port_display",
        verbose_name=_("Collector Port"),
        link=lambda tm: _port_url(tm.remote_port_id))
    direction = tables.Column(
        "direction_display",
        verbose_name=_("Direction"))
    mirror_type = tables.Column(
        "mirror_type",
        verbose_name=_("Type"))

    class Meta(object):
        name = "tap_mirrors"
        verbose_name = _("Tap Mirrors")
        table_actions = (CreateTapMirror, DeleteTapMirror)
        row_actions = (DeleteTapMirror,)
