from saml2 import md, assertion
from saml2.saml import Attribute, NAME_FORMAT_URI, AttributeValue
from saml2.assertion import Policy, Assertion, filter_on_attributes
from saml2.assertion import filter_attribute_value_assertions
from saml2.utils import MissingValue

from py.test import raises

def _eq(l1,l2):
    return set(l1) == set(l2)

gn = md.RequestedAttribute(
    name="urn:oid:2.5.4.42",
    friendly_name="givenName",
    name_format=NAME_FORMAT_URI)

sn = md.RequestedAttribute(
    name="urn:oid:2.5.4.4",
    friendly_name="surName",
    name_format=NAME_FORMAT_URI)

mail = md.RequestedAttribute(
    name="urn:oid:0.9.2342.19200300.100.1.3",
    friendly_name="mail",
    name_format=NAME_FORMAT_URI)

# ---------------------------------------------------------------------------

def test_combine_0():
    r = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber")    
    o = Attribute(name="urn:oid:2.5.4.4", name_format=NAME_FORMAT_URI,
                    friendly_name="surName")

    comb = assertion._combine([r],[o])
    print comb
    assert _eq(comb.keys(), [('urn:oid:2.5.4.5', 'serialNumber'), 
                                ('urn:oid:2.5.4.4', 'surName')])
    assert comb[('urn:oid:2.5.4.5', 'serialNumber')] == ([], [])
    assert comb[('urn:oid:2.5.4.4', 'surName')] == ([], [])

def test_filter_on_attributes_0():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber")    
    
    required = [a]
    ava = { "serialNumber": ["12345"]}
    
    ava = filter_on_attributes(ava, required)
    assert ava.keys() == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]

def test_filter_on_attributes_1():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber")    
    
    required = [a]
    ava = { "serialNumber": ["12345"], "givenName":["Lars"]}
    
    ava = filter_on_attributes(ava, required)
    assert ava.keys() == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]


# ----------------------------------------------------------------------

def test_lifetime_1():
    conf = {
            "default": {
                "lifetime": {"minutes":15},
                "attribute_restrictions": None # means all I have
            },
            "urn:mace:umu.se:saml:roland:sp": {
                "lifetime": {"minutes": 5},
                "attribute_restrictions":{
                    "givenName": None,
                    "surName": None,
                    "mail": [".*@.*\.umu\.se"],
                }
            }}
    
    r = Policy(conf)
    assert r != None
    
    assert r.get_lifetime("urn:mace:umu.se:saml:roland:sp") == {"minutes": 5}               
    assert r.get_lifetime("urn:mace:example.se:saml:sp") == {"minutes": 15}
    
def test_lifetime_2():
    conf = {
            "default": {
                "attribute_restrictions": None # means all I have
            },
            "urn:mace:umu.se:saml:roland:sp": {
                "lifetime": {"minutes": 5},
                "attribute_restrictions":{
                    "givenName": None,
                    "surName": None,
                    "mail": [".*@.*\.umu\.se"],
                }
            }}
    
    r = Policy(conf)
    assert r != None
    
    assert r.get_lifetime("urn:mace:umu.se:saml:roland:sp") == {"minutes": 5}               
    assert r.get_lifetime("urn:mace:example.se:saml:sp") == {"hours": 1}        
    
    
    
def test_ava_filter_1():
    conf = {
        "default": {
            "lifetime": {"minutes":15},
            "attribute_restrictions": None # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions":{
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    r = Policy(conf)
    
    ava = {"givenName":"Derek", 
            "surName": "Jeter", 
            "mail":"derek@example.com"}
    
    ava = r.filter(ava,"urn:mace:umu.se:saml:roland:sp",None,None)
    assert _eq(ava.keys(), ["givenName","surName"])

    ava = {"givenName":"Derek", 
            "mail":"derek@nyy.umu.se"}

    assert _eq(ava.keys(), ["givenName","mail"])

def test_ava_filter_2():
    conf = {
        "default": {
            "lifetime": {"minutes":15},
            "attribute_restrictions": None # means all I have
        },
        "urn:mace:umu.se:saml:roland:sp": {
            "lifetime": {"minutes": 5},
            "attribute_restrictions":{
                "givenName": None,
                "surName": None,
                "mail": [".*@.*\.umu\.se"],
            }
        }}

    r = Policy(conf)
    
    ava = {"givenName":"Derek", 
            "surName": "Jeter", 
            "mail":"derek@example.com"}
            
    # I'm filtering away something the SP deems necessary
    raises(MissingValue, r.filter, ava, 'urn:mace:umu.se:saml:roland:sp',
                 [mail], [gn, sn])

    ava = {"givenName":"Derek", 
            "surName": "Jeter"}

    # it wasn't there to begin with
    raises(MissingValue, r.filter, ava, 'urn:mace:umu.se:saml:roland:sp',
                [gn,sn,mail])

def test_filter_attribute_value_assertions_0(AVA):    
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "surName": [".*berg"],
            }
        }
    })
    
    ava = filter_attribute_value_assertions(AVA[3].copy(), 
                                            p.get_attribute_restriction(""))
    
    print ava
    assert ava.keys() == ["surName"]
    assert ava["surName"] == ["Hedberg"]

def test_filter_attribute_value_assertions_1(AVA):
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "surName": None,
                "givenName": [".*er.*"],
            }
        }
    })
        
    ava = filter_attribute_value_assertions(AVA[0].copy(), 
                                            p.get_attribute_restriction(""))
    
    print ava
    assert _eq(ava.keys(), ["givenName","surName"])
    assert ava["surName"] == ["Jeter"]
    assert ava["givenName"] == ["Derek"]

    ava = filter_attribute_value_assertions(AVA[1].copy(),
                                            p.get_attribute_restriction(""))
    
    print ava
    assert _eq(ava.keys(), ["surName"])
    assert ava["surName"] == ["Howard"]
    
    
def test_filter_attribute_value_assertions_2(AVA):
    p = Policy({
        "default": {
            "attribute_restrictions": {
                "givenName": ["^R.*"],
            }
        }
    })
    
    ava = filter_attribute_value_assertions(AVA[0].copy(), 
                                            p.get_attribute_restriction(""))
    
    print ava
    assert _eq(ava.keys(), [])
    
    ava = filter_attribute_value_assertions(AVA[1].copy(), 
                                            p.get_attribute_restriction(""))
    
    print ava
    assert _eq(ava.keys(), ["givenName"])
    assert ava["givenName"] == ["Ryan"]

    ava = filter_attribute_value_assertions(AVA[3].copy(), 
                                            p.get_attribute_restriction(""))
    
    print ava
    assert _eq(ava.keys(), ["givenName"])
    assert ava["givenName"] == ["Roland"]

# ----------------------------------------------------------------------------

def test_assertion_1(AVA):
    ava = Assertion(AVA[0])
    
    print ava
    print ava.__dict__

    policy = Policy({
        "default": {
            "attribute_restrictions": {
                "givenName": ["^R.*"],
            }
        }
    })

    ava = ava.apply_policy( "", policy )
    
    print ava
    assert _eq(ava.keys(), [])

    ava = Assertion(AVA[1].copy())
    ava = ava.apply_policy( "", policy )
    assert _eq(ava.keys(), ["givenName"])
    assert ava["givenName"] == ["Ryan"]

    ava = Assertion(AVA[3].copy())
    ava = ava.apply_policy( "", policy )
    assert _eq(ava.keys(), ["givenName"])
    assert ava["givenName"] == ["Roland"]
    
# ----------------------------------------------------------------------------
    
def test_filter_values_req_2():
    a1 = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber")    
    a2 = Attribute(name="urn:oid:2.5.4.4", name_format=NAME_FORMAT_URI,
                    friendly_name="surName")
    
    required = [a1,a2]
    ava = { "serialNumber": ["12345"], "givenName":["Lars"]}
    
    raises(MissingValue, filter_on_attributes, ava, required)

def test_filter_values_req_3():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="12345")])    
    
    required = [a]
    ava = { "serialNumber": ["12345"]}
    
    ava = filter_on_attributes(ava, required)
    assert ava.keys() == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]

def test_filter_values_req_4():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="54321")])    
    
    required = [a]
    ava = { "serialNumber": ["12345"]}
    
    raises(MissingValue, filter_on_attributes, ava, required)

def test_filter_values_req_5():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="12345")])    
    
    required = [a]
    ava = { "serialNumber": ["12345", "54321"]}
    
    ava = filter_on_attributes(ava, required)
    assert ava.keys() == ["serialNumber"]
    assert ava["serialNumber"] == ["12345"]

def test_filter_values_req_6():
    a = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="54321")])    
    
    required = [a]
    ava = { "serialNumber": ["12345", "54321"]}
    
    ava = filter_on_attributes(ava, required)
    assert ava.keys() == ["serialNumber"]
    assert ava["serialNumber"] == ["54321"]

def test_filter_values_req_opt_0():
    r = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="54321")])    
    o = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="12345")])    
    
    ava = { "serialNumber": ["12345", "54321"]}
    
    ava = filter_on_attributes(ava, [r], [o])
    assert ava.keys() == ["serialNumber"]
    assert _eq(ava["serialNumber"], ["12345","54321"])

def test_filter_values_req_opt_1():
    r = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="54321")])    
    o = Attribute(name="urn:oid:2.5.4.5", name_format=NAME_FORMAT_URI,
                    friendly_name="serialNumber", attribute_value=[
                        AttributeValue(text="12345"),
                        AttributeValue(text="abcd0")])    
    
    ava = { "serialNumber": ["12345", "54321"]}
    
    ava = filter_on_attributes(ava, [r], [o])
    assert ava.keys() == ["serialNumber"]
    assert _eq(ava["serialNumber"], ["12345","54321"])
    
# ---------------------------------------------------------------------------


def test_filter_ava_0():
    policy = Policy({
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None # means all I have
                },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                }
            })
            
    ava = { "givenName": ["Derek"], "surName": ["Jeter"], 
            "mail": ["derek@nyy.mlb.com"]}
    
    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp",
                            [], [])
                                
    assert _eq(ava.keys(), ["givenName", "surName", "mail"])
    assert ava["givenName"] == ["Derek"]
    assert ava["surName"] == ["Jeter"]
    assert ava["mail"] == ["derek@nyy.mlb.com"]
        
        
def test_filter_ava_1():
    """ No mail address returned """
    policy = Policy({
            "default": {
                "lifetime": {"minutes":15},
                "attribute_restrictions": None # means all I have
            },
            "urn:mace:example.com:saml:roland:sp": {
                "lifetime": {"minutes": 5},
                "attribute_restrictions":{
                    "givenName": None,
                    "surName": None,
                }
            }})
    
    ava = { "givenName": ["Derek"], "surName": ["Jeter"], 
            "mail": ["derek@nyy.mlb.com"]}
    
    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])
                                
    assert _eq(ava.keys(), ["givenName", "surName"])
    assert ava["givenName"] == ["Derek"]
    assert ava["surName"] == ["Jeter"]

def test_filter_ava_2():
    """ Only mail returned """
    policy = Policy({
            "default": {
                "lifetime": {"minutes":15},
                "attribute_restrictions": None # means all I have
            },
            "urn:mace:example.com:saml:roland:sp": {
                "lifetime": {"minutes": 5},
                "attribute_restrictions":{
                    "mail": None,
                }
            }})
    
    ava = { "givenName": ["Derek"], "surName": ["Jeter"], 
            "mail": ["derek@nyy.mlb.com"]}
    
    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])
                                
    assert _eq(ava.keys(), ["mail"])
    assert ava["mail"] == ["derek@nyy.mlb.com"]

def test_filter_ava_3():
    """ Only example.com mail addresses returned """
    policy = Policy({
            "default": {
                "lifetime": {"minutes":15},
                "attribute_restrictions": None # means all I have
            },
            "urn:mace:example.com:saml:roland:sp": {
                "lifetime": {"minutes": 5},
                "attribute_restrictions":{
                    "mail": [".*@example\.com$"],
                }
            }})
    
    ava = { "givenName": ["Derek"], "surName": ["Jeter"], 
            "mail": ["derek@nyy.mlb.com", "dj@example.com"]}
    
    # No restrictions apply
    ava = policy.filter(ava, "urn:mace:example.com:saml:roland:sp", [], [])
                                
    assert _eq(ava.keys(), ["mail"])
    assert ava["mail"] == ["dj@example.com"]