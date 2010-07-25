#!/usr/bin/env python

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

import saml2.samlp as samlp
from saml2.samlp import NAMESPACE as SAMLP_NAMESPACE

NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"

example = """<Envelope xmlns="http://schemas.xmlsoap.org/soap/envelope/">
    <Body>
        <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" 
            xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" 
            ID="_6c3a4f8b9c2d" Version="2.0" IssueInstant="2004-03-27T08:42:00Z">
        <saml:Issuer>https://www.example.com/SAML</saml:Issuer>
        <Status>
        <StatusCode Value='urn:oasis:names:tc:SAML:2.0:status:Success'/>
        </Status>
        <saml:Assertion>
        <saml:Subject></saml:Subject>
        <saml:AttributeStatement></saml:AttributeStatement>
        </saml:Assertion>
        </samlp:Response>
    </Body>
</Envelope>
"""

def test_parse_soap_envelope():
    envelope = ElementTree.fromstring(example)
    assert envelope.tag == '{%s}Envelope' % NAMESPACE
    # How to check that it's the right type ?
    assert len(envelope) == 1
    body = envelope[0]
    assert body.tag == '{%s}Body' % NAMESPACE
    assert len(body) == 1
    saml_part = body[0]
    assert saml_part.tag == '{%s}Response' % SAMLP_NAMESPACE
    # {http://schemas.xmlsoap.org/soap/envelope/}Envelope

def test_make_soap_envelope():
    envelope = ElementTree.Element('')
    envelope.tag = '{%s}Envelope' % NAMESPACE
    
    body = ElementTree.Element('')
    body.tag = '{%s}Body' % NAMESPACE
    
    envelope.append(body)
    
    request = samlp.AuthnRequest()
    request.become_child_element_of(body)
    
    string = ElementTree.tostring(envelope, encoding="UTF-8")
    result = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"><ns0:Body><ns1:AuthnRequest xmlns:ns1="urn:oasis:names:tc:SAML:2.0:protocol" /></ns0:Body></ns0:Envelope>"""
    assert string == result