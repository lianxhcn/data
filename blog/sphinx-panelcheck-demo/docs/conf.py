from importlib.metadata import version as package_version
project = 'panelcheck_demo'
author = '连享会'
release = package_version('panelcheck-demo')
version = release
extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.napoleon', 'sphinx.ext.doctest', 'sphinx.ext.githubpages']
source_suffix = {'.md': 'markdown', '.rst': 'restructuredtext'}
autosummary_generate = True
autodoc_typehints = 'none'
html_theme = 'pydata_sphinx_theme'
html_theme_options = {'show_nav_level': 2, 'navigation_depth': 3}
html_sidebars = {'**': ['search-field.html', 'sidebar-nav-bs.html']}
language = 'zh_CN'
exclude_patterns = ['_build']
linkcheck_timeout = 20
linkcheck_retries = 1


# Sphinx 9.0.4 中文索引生成的 ChineseStemmer 未定义，使用英文/API 检索。
html_search_language = 'en'

templates_path = ['_templates']
html_sidebars = {'**': ['search-field.html', 'all-sections.html']}
