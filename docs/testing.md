# Testing bootstapper

Bootstrapper uses the pytest framework for unit testing

execute all tests with:
```baash
cd bootstrapper
python -m pytest tests

```

You can also call it like this if desired:

```bash
PYTHONPATH=. pytest

```

## Example test output

```bash
(venv) DFWMACK0AJHTDG:panos_bootstrapper nembery$ PYTHONPATH=. pytest -v
=============================================================================================================== test session starts ===============================================================================================================
platform darwin -- Python 2.7.10, pytest-3.5.1, py-1.5.3, pluggy-0.6.0 -- /Users/nembery/PycharmProjects/panos_bootstrapper/venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/nembery/PycharmProjects/panos_bootstrapper, inifile:
collected 6 items                                                                                                                                                                                                                                 

tests/test_bootstrapper.py::test_index PASSED                                                                                                                                                                                               [ 16%]
tests/test_bootstrapper.py::test_caching PASSED                                                                                                                                                                                             [ 33%]
tests/test_bootstrapper.py::test_build_openstack_bootstrap PASSED                                                                                                                                                                           [ 50%]
tests/test_bootstrapper.py::test_build_base_configs PASSED                                                                                                                                                                                  [ 66%]
tests/test_bootstrapper.py::test_build_openstack_configs PASSED                                                                                                                                                                             [ 83%]
tests/test_bootstrapper.py::test_build_openstack_archive PASSED                                                                                                                                                                             [100%]

============================================================================================================ 6 passed in 0.26 seconds =============================================================================================================
(venv) DFWMACK0AJHTDG:panos_bootstrapper nembery$ 

```