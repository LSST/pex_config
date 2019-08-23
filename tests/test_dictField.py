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
import lsst.pex.config as pexConfig


class Config1(pexConfig.Config):
    d1 = pexConfig.DictField("d1", keytype=str, itemtype=int, default={"hi": 4}, itemCheck=lambda x: x > 0)
    d2 = pexConfig.DictField("d2", keytype=str, itemtype=str, default=None)
    d3 = pexConfig.DictField("d3", keytype=float, itemtype=float, optional=True, itemCheck=lambda x: x > 0)
    d4 = pexConfig.DictField("d4", keytype=str, itemtype=None, default={})


class DictFieldTest(unittest.TestCase):
    def testConstructor(self):
        try:
            class BadKeytype(pexConfig.Config):
                d = pexConfig.DictField("...", keytype=list, itemtype=int)
        except Exception:
            pass
        else:
            raise SyntaxError("Unsupported keyptype DictFields should not be allowed")

        try:
            class BadItemtype(pexConfig.Config):
                d = pexConfig.DictField("...", keytype=int, itemtype=dict)
        except Exception:
            pass
        else:
            raise SyntaxError("Unsupported itemtype DictFields should not be allowed")

        try:
            class BadItemCheck(pexConfig.Config):
                d = pexConfig.DictField("...", keytype=int, itemtype=int, itemCheck=4)
        except Exception:
            pass
        else:
            raise SyntaxError("Non-callable itemCheck DictFields should not be allowed")

        try:
            class BadDictCheck(pexConfig.Config):
                d = pexConfig.DictField("...", keytype=int, itemtype=int, dictCheck=4)
        except Exception:
            pass
        else:
            raise SyntaxError("Non-callable dictCheck DictFields should not be allowed")

    def testAssignment(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "d1", {3: 3})
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "d1", {"a": 0})
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "d1", [1.2, 3, 4])
        c.d1 = None
        c.d1 = {"a": 1, "b": 2}
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "d3", {"hi": True})
        c.d3 = {4: 5}
        self.assertEqual(c.d3, {4.: 5.})
        d = {"a": None, "b": 4, "c": "foo"}
        c.d4 = d
        self.assertEqual(c.d4, d)
        c.d4["a"] = 12
        c.d4[u"b"] = "three"
        c.d4["c"] = None
        self.assertEqual(c.d4["a"], 12)
        self.assertEqual(c.d4["b"], "three")
        self.assertEqual(c.d4["c"], None)
        self.assertRaises(pexConfig.FieldValidationError, setattr, c, "d4", {"hi": [1, 2, 3]})

    def testValidate(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, Config1.validate, c)

        c.d2 = {"a": "b"}
        c.validate()

    def testInPlaceModification(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, c.d1.__setitem__, 2, 0)
        self.assertRaises(pexConfig.FieldValidationError, c.d1.__setitem__, "hi", 0)
        c.d1["hi"] = 10
        self.assertEqual(c.d1, {"hi": 10})

        c.d3 = {}
        c.d3[4] = 5
        self.assertEqual(c.d3, {4.: 5.})

    def testNoArbitraryAttributes(self):
        c = Config1()
        self.assertRaises(pexConfig.FieldValidationError, setattr, c.d1, "should", "fail")

    def testEquality(self):
        """Test DictField.__eq__

        We create two dicts, with the keys explicitly added in a different order
        and test their equality.
        """
        keys1 = ['A', 'B', 'C']
        keys2 = ['X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e']

        c1 = Config1()
        c1.d4 = {k: "" for k in keys1}
        for k in keys2:
            c1.d4[k] = ""

        c2 = Config1()
        for k in keys2 + keys1:
            c2.d4[k] = ""

        self.assertTrue(pexConfig.compareConfigs('test', c1, c2))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
