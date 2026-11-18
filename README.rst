======================
Neutron TaaS Dashboard
======================

OpenStack Dashboard panels for Neutron Tap-as-a-Service (TaaS) tap mirrors.

* Documentation: ``doc/source`` (``tox -e docs``)
* Source: https://github.com/ycy1766/neutron-taas-dashboard
* Bugs: https://github.com/ycy1766/neutron-taas-dashboard/issues
* Release Notes: ``releasenotes`` (``tox -e releasenotes``)

The project is maintained on GitHub, outside of OpenStack, and follows the
layout and conventions of the OpenStack Horizon plugins (for example
``neutron-vpnaas-dashboard``) so that it builds, tests and documents the
same way. See ``CONTRIBUTING.rst``.

Features
--------

* **Project > Network > Tap Mirrors** panel: list, create, show and delete
  ``lport`` tap mirrors, which copy the traffic of one VM port to another
  VM port of the same project (``tap-mirror-lport`` Neutron extension).
* Port choices show the server, network, IP addresses and port name instead
  of bare UUIDs.
* The panel is only shown when Neutron advertises the extension; the Create
  and Delete actions follow the ``create_tap_mirror`` and
  ``delete_tap_mirror`` policy rules.

See the installation and configuration guides under ``doc/source`` for the
requirements, the policy file and the limits of the current version.
