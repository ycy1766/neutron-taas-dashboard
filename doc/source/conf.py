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

import os
import sys

PROJECT = 'neutron-taas-dashboard'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

sys.path.insert(0, ROOT)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'reno.sphinxext',
]


templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'Neutron TaaS Dashboard'
copyright = u'2026, Chanyeol Yoon'

exclude_patterns = ['**/#*', '**~', '**/#*#']
show_authors = False
pygments_style = 'native'
modindex_common_prefix = ['neutron_taas_dashboard.']
primary_domain = 'py'
nitpicky = False

html_theme = 'alabaster'
html_static_path = []
htmlhelp_basename = 'neutrontaasdashboarddoc'

latex_documents = [
    ('index', 'doc-neutron-taas-dashboard.tex',
     u'Neutron TaaS Dashboard Documentation',
     u'Neutron Contributors', 'howto'),
]
