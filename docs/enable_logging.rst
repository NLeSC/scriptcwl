Enable logging for debugging
============================

If you get errors while creating workflows, and scriptcwl doesn't give you a
proper error message, you might want to enable logging to try and figure out
what goes wrong.

To enable logging, do:

::

  import logging
  logging.basicConfig(format="%(asctime)s [%(process)d] %(levelname)-8s "
                      "%(name)s,%(lineno)s\t%(message)s")
  logging.getLogger().setLevel('DEBUG')
