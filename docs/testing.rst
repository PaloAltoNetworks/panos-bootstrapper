Testing
=======

Bootstrapper uses the pytest framework for unit testing


Executing Tests
---------------

execute all tests with:

.. code-block:: bash

    cd bootstrapper
    python -m pytest tests

You can also call it like this if desired:


.. code-block:: bash

    PYTHONPATH=. pytest -v


Example test output
-------------------

.. code-block:: bash

    (panos-bootstrapper) DFWMACK0AJHTDG:panos-bootstrapper nembery$ python -m pytest tests -v
    ============================================== test session starts ==============================================
    platform darwin -- Python 3.6.5, pytest-3.5.1, py-1.5.3, pluggy-0.6.0 -- /Users/nembery/PycharmProjects/panos_license_tool/panos-bootstrapper/bin/python
    cachedir: .pytest_cache
    rootdir: /Users/nembery/PycharmProjects/panos-bootstrapper, inifile:
    collected 8 items

    tests/test_bootstrapper.py::test_index PASSED                                                             [ 12%]
    tests/test_bootstrapper.py::test_caching PASSED                                                           [ 25%]
    tests/test_bootstrapper.py::test_build_openstack_archive PASSED                                           [ 37%]
    tests/test_bootstrapper.py::test_get_bootstrap_variables PASSED                                           [ 50%]
    tests/test_bootstrapper.py::test_import_template PASSED                                                   [ 62%]
    tests/test_bootstrapper.py::test_get_template PASSED                                                      [ 75%]
    tests/test_bootstrapper.py::test_list_templates PASSED                                                    [ 87%]
    tests/test_bootstrapper.py::test_delete_template PASSED                                                   [100%]

    =========================================== 8 passed in 0.41 seconds ============================================
    (panos-bootstrapper) DFWMACK0AJHTDG:panos-bootstrapper nembery$
