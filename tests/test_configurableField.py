# This file is part of pex_config.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.

import os
import unittest
import lsst.pex.config as pexConf


class Config1(pexConf.Config):
    f = pexConf.Field("f", dtype=float, default=5, check=lambda x: x > 0)


class Target1:
    ConfigClass = Config1

    def __init__(self, config):
        self.f = config.f


def Target2(config):
    return config.f


class Config2(pexConf.Config):
    c1 = pexConf.ConfigurableField("c1", target=Target1)
    c2 = pexConf.ConfigurableField("c2", target=Target2, ConfigClass=Config1, default=Config1(f=3))


class ConfigurableFieldTest(unittest.TestCase):
    def testConstructor(self):
        try:
            class BadTarget(pexConf.Config):
                d = pexConf.ConfigurableField("...", target=None)
        except Exception:
            pass
        else:
            raise SyntaxError("Uncallable targets should not be allowed")

        try:
            class NoConfigClass(pexConf.Config):
                d = pexConf.ConfigurableField("...", target=Target2)
        except Exception:
            pass
        else:
            raise SyntaxError("Missing ConfigClass should not be allowed")

        try:
            class BadConfigClass(pexConf.Config):
                d = pexConf.DictField("...", target=Target2, ConfigClass=Target2)
        except Exception:
            pass
        else:
            raise SyntaxError("ConfigClass that are not subclasses of Config should not be allowed")

    def testBasics(self):
        c = Config2()
        self.assertEqual(c.c1.f, 5)
        self.assertEqual(c.c2.f, 3)

        self.assertEqual(type(c.c1.apply()), Target1)
        self.assertEqual(c.c1.apply().f, 5)
        self.assertEqual(c.c2.apply(), 3)

        c.c2.retarget(Target1)
        self.assertEqual(c.c2.f, 3)
        self.assertEqual(type(c.c2.apply()), Target1)
        self.assertEqual(c.c2.apply().f, 3)

        c.c1.f = 2
        self.assertEqual(c.c1.f, 2)
        self.assertRaises(pexConf.FieldValidationError, setattr, c.c1, "f", 0)

        c.c1 = Config1(f=10)
        self.assertEqual(c.c1.f, 10)

        c.c1 = Config1
        self.assertEqual(c.c1.f, 5)

        f = Config2(**dict(c.items()))
        self.assertEqual(f.c1.f, c.c1.f)
        self.assertEqual(f.c1.target, c.c1.target)
        self.assertEqual(f.c2.target, c.c2.target)
        self.assertEqual(f.c2.f, c.c2.f)

        c.c2.f = 1
        c.c1.f = 100
        f.update(**dict(c.items()))
        self.assertEqual(f.c1.f, c.c1.f)
        self.assertEqual(f.c1.target, c.c1.target)
        self.assertEqual(f.c2.target, c.c2.target)
        self.assertEqual(f.c2.f, c.c2.f)

    def testValidate(self):
        c = Config2()
        self.assertRaises(pexConf.FieldValidationError, setattr, c.c1, "f", 0)

        c.validate()

    def testPersistence(self):
        c = Config2()
        c.c2.retarget(Target1)
        c.c2.f = 10
        c.save("test.py")

        r = Config2()
        r.load("test.py")
        os.remove("test.py")

        self.assertEqual(c.c2.f, r.c2.f)
        self.assertEqual(c.c2.target, r.c2.target)


if __name__ == "__main__":
    unittest.main()
