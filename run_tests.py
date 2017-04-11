#!/usr/bin/env python

import logging
import unittest

logging.disable(logging.CRITICAL)


def main():
    suite = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()
