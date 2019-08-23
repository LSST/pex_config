# This file is part of pex_config.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import lsst.utils.tests
import lsst.pex.config as pexConf


class Config1(pexConf.Config):
    f = pexConf.Field("Config1.f", float, default=4)


class Config2(Config1):
    def setDefaults(self):
        self.f = 5


class Config3(Config1):

    def __init__(self, **kw):
        self.f = 6


class SquashingDefaultsTest(unittest.TestCase):
    def test(self):
        c1 = Config1()
        self.assertEqual(c1.f, 4)
        c1 = Config1(f=9)
        self.assertEqual(c1.f, 9)

        c2 = Config2()
        self.assertEqual(c2.f, 5)
        c2 = Config2(f=10)
        self.assertEqual(c2.f, 10)

        c3 = Config3()
        self.assertEqual(c3.f, 6)
        c3 = Config3(f=11)
        self.assertEqual(c3.f, 6)


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
