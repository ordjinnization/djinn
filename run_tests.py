#!/usr/bin/env python

import logging
import unittest

logging.disable(logging.CRITICAL)


def main():
    suite = unittest.TestLoader().discover('tests')
    run = unittest.TextTestRunner().run(suite)
    if not run.wasSuccessful():
        exit(1)


if __name__ == '__main__':
    main()
