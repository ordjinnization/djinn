#!/usr/bin/env python

import unittest


def main():
    suite = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()