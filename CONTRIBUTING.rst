============
Contributing
============

The project is maintained on GitHub and is not part of OpenStack. The
workflow is:

* Report bugs and propose changes through the GitHub repository
  https://github.com/ycy1766/neutron-taas-dashboard. Pull requests must pass
  the ``ci`` workflow (``flake8`` and the unit tests against the supported
  Horizon release).
* Sign your commits (``git commit -s``). The Developer Certificate of Origin
  applies as in OpenStack.
* Follow the OpenStack style and commit message conventions:
  https://docs.openstack.org/hacking/latest/user/hacking.html and
  https://wiki.openstack.org/wiki/GitCommitMessages.
* Add a release note under ``releasenotes/notes`` with ``reno new <slug>``
  for user visible changes.
