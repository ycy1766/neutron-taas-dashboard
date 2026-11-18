==========================================
Neutron TaaS Dashboard Style Commandments
==========================================

Read the OpenStack Style Commandments
https://docs.openstack.org/hacking/latest/user/hacking.html

Project Specific Commandments
-----------------------------

- Read the Horizon contributing documentation at
  https://docs.openstack.org/horizon/latest/contributor/contributing.html
- All calls to Neutron live in ``neutron_taas_dashboard/api/taas.py``.
  Views, forms and tables never build a client themselves.
- [M322] Method's default argument shouldn't be mutable.
