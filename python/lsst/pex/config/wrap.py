from .config import *

import re

__all__ = ("wrap", "makeConfigClass")

_dtypeMap = {
    "bool": bool,
    "int": int,
    "double": float,
    "float": float,
    "std::string": str
}

_containerRegex = re.compile(r"(std::)?(vector|list)<\s*(?P<type>[a-z:]+)\s*>")

def makeConfigClass(ctrl, name=None, base=Config, doc=None, cls=None):
    """A function that creates a Python config class that matches a  C++ control object class.

    @param ctrl   C++ control class to wrap.
    @param name   Name of the new config class; defaults to the __name__ of the control
                  class with 'Control' replaced with 'Config'
    @param base   Base class for the config class.
    @param doc    Docstring for the config class.
    @param cfg    An existing config class to use instead of creating a new one; name, base
                  and doc will be ignored if this is not None.

    See the 'wrap' decorator as a way to use makeConfigClass that may be more convenient.

    To use makeConfigClass, in C++, write a control object, using the LSST_CONTROL_FIELD macro in
    lsst/pex/config.h (note that it must have sensible default constructor):

    struct FooControl {
        LSST_CONTROL_FIELD(bar, int, "documentation for field 'bar'");
        LSST_CONTROL_FIELD(baz, double, "documentation for field 'baz'");

        FooControl() : bar(0), baz(0.0) {}
    };

    Swig that control object.  Now, in Python, do this:

    import mySwigLib
    import lsst.pex.config
    FooConfig = lsst.pex.config.makeConfigClass(
    @lsst.pex.config.wrap(mySwigLib.FooControl)
    class FooConfig:
        pass

    This will add fully-fledged "bar" and "baz" fields to FooConfig, set
    FooConfig.Control = FooControl, and inject makeControl and readControl
    methods to create a FooControl and set the FooConfig from the FooControl,
    respectively.  In addition, if FooControl has a validate() member function,
    a custom validate() method will be added to FooConfig that uses it.
    
    Note that the injected fields and methods will override any fields and methods
    of the same name that are manually added to FooConfig, but the user can
    add additional fields, methods, or properties to FooConfig as usual.

    While LSST_CONTROL_FIELD will work for any C++ type, automatic Config generation
    only supports bool, int, double, and std::string fields, along with std::list
    and std::vectors of those types.  Nested control objects are not supported.
    """
    if name is None:
        name = ctrl.__name__.replace("Control", "Config")
    if cls is None:
        cls = type(name, (base,), {"__doc__":doc})
    if doc is None:
        doc = ctrl.__doc__
    fields = {}
    for attr in dir(ctrl):
        if attr.startswith("_type_"):
            k = attr[6:]
            getDoc = "_doc_" + k
            getType = attr
            if hasattr(ctrl, k) and hasattr(ctrl, getDoc):
                doc = getattr(ctrl, getDoc)()
                ctype = getattr(ctrl, getType)()
                try:
                    dtype = _dtypeMap[ctype]
                    FieldCls = Field
                except KeyError:
                    dtype = None
                    m = _containerRegex.match(ctype)
                    if m:
                        dtype = _dtypeMap.get(m.group("type"), None)
                        FieldCls = ListField
                if dtype is None:
                    raise TypeError("Could not parse field type '%s'." % ctype)
                fields[k] = FieldCls(doc=doc, dtype=dtype, optional=True)
    def makeControl(self):
        """Construct a C++ Control object from this Config object.

        Fields set to None will be ignored, and left at the values defined by the
        Control object's default constructor.
        """
        r = self.Control()
        for k in fields:
            value = getattr(self, k)
            if value is not None:
                setattr(r, k, value)
        return r
    def readControl(self, control):
        """Read values from a C++ Control object and assign them to self's fields.
        """
        for k in fields:
            setattr(self, k, getattr(control, k))
    def validate(self):
        """Validate the config object by constructing a control object and using
        a C++ validate() implementation."""
        super(cls, self).validate()
        r = self.makeControl()
        r.validate()
    def __init__(self, **kw):
        """Initialize the config object, using the Control objects default ctor
        to provide defaults."""
        r = self.Control()
        defaults = {}
        for k in fields:
            value = getattr(r, k)
            defaults[k] = value
        super(cls, self).__init__(**defaults)
        self.update(**kw)
    ctrl.ConfigClass = cls
    cls.Control = ctrl
    cls.makeControl = makeControl
    cls.readControl = readControl
    cls.__init__ = __init__
    if hasattr(ctrl, "validate"):
        cls.validate = validate
    for k, field in fields.iteritems():
        setattr(cls, k, field)
    return cls

def wrap(ctrl):
    """A decorator that adds fields from a C++ control class to a Python config class.

    Used like this:

    @wrap(MyControlClass)
    class MyConfigClass(Config):
        pass

    See makeConfigClass for more information.
    """
    def decorate(cls):
        return makeConfigClass(ctrl, cls=cls)
    return decorate
