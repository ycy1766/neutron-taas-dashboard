..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

==========
User Guide
==========

The **Project > Network > Tap Mirrors** panel manages ``lport`` tap mirrors
of the current project. An ``lport`` tap mirror copies the traffic of one
Neutron port (the *source port*) to another Neutron port of the same
project (the *collector port*), for example the port of an IDS or packet
capture instance. The copy is made by OVN inside the overlay; no tunnel to
an external destination is needed.

Creating a tap mirror
---------------------

Click **Create Tap Mirror** and fill in:

Name, Description
    Optional.

Source Port
    The VM port whose traffic is copied. The choices show the server name,
    the network, the fixed IP addresses and the port name (or the first
    characters of the port id).

Collector Port
    The VM port that receives the copies. It must belong to the current
    project and must differ from the source port.

Direction
    *Both directions*, *Ingress* (traffic going to the source port) or
    *Egress* (traffic leaving the source port). Egress is copied before the
    security groups of the source port are applied, ingress after them. The
    copies bypass the security groups, QoS and connection tracking of the
    collector port.

The source port, the collector port and the direction can not be changed
after creation: delete the tap mirror and create a new one.

A successful creation means that the mirror was recorded by Neutron. The
panel does not show whether packets are actually being delivered.

Limits of the current version
-----------------------------

* Only ``lport`` tap mirrors are listed and offered for deletion. Mirrors of
  type ``gre`` and ``erspanv1`` created through the API or the CLI are shown
  read-only when opened by their URL.
* Only ports with a ``compute:*`` device owner are offered as source and
  collector. This is a restriction of the panel, not of the Neutron API.
* The server name in a port choice comes from a single Nova list call, which
  Nova caps at ``osapi_max_limit`` (1000 by default). In a larger project
  the remaining ports are labelled with the server id.
* Tap mirror rules (match based filtering of what is copied) are not
  supported yet.
