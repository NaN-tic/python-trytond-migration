# -*- coding: utf-8 -*-

import stdnum.eu.vat as vat

from trytond.pool import Pool
from .common import create_model


def create_party(party_dict):
    return create_model('party.party', **party_dict)


def party_exists_by_name(name):
    Party = Pool().get('party.party')
    parties = Party.search(('name', '=', name), limit=1)
    if parties:
        return parties[0]


def party_exists_by_code(code):
    return party_exists_by_identifier(code, 'migration')


def party_exists_by_vat(vat_code, country='ES'):
    vat_code = vat_code.upper().strip().replace('-', '')

    if not vat_code:
        return None

    if country:
        vat_code = country + vat_code

    if not vat.is_valid(vat_code):
        return None

    vat_code = vat.compact(vat_code)

    parties = party_exists_by_identifier(vat_code)
    if parties:
        return parties[0]

    return False


def party_exists_by_identifier(code, type='eu_vat'):
    PartyId = Pool().get('party.identifier')
    parties = PartyId.search([('code', '=', code), ('type', '=', type)],
        limit=1)
    if parties:
        return parties
    return None


def create_address(values):
    zips = get_zip(values.get('zip'))
    # TODO
    values['country'] = None
    values['subdivision'] = None
    if zips:
        values.update({'country': zips.country,
            'subdivision': zips.subdivision})

    return create_model('party.address', **values)


def get_zip(zip_code):
    CountryZip = Pool().get('country.zip')
    zips = CountryZip.search([('zip', '=', zip_code)], limit=1)
    if zips:
        return zips[0]


def create_vat(code, country='ES'):
    vat_code = code.upper().strip().replace('-', '')
    if country:
        vat_code = country + vat_code

    vat_code = vat.compact(vat_code)

    values = {}
    values['code'] = vat_code
    values['type'] = 'migration'
    if vat.is_valid(vat_code):
        values['type'] = 'eu_vat'

    return create_model('party.identifier', **values)


def create_identifier(code, type):
    values = {
        'code': code,
        'type': type
    }
    return create_model('party.identifier', **values)


def create_contact_mechanism(values):
    return create_model('party.contact_mechanism', **values)
