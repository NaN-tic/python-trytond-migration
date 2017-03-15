# -*- coding: utf-8 -*-

import stdnum.eu.vat as vat

from trytond.pool import Pool


def create_model(model_name,  **kwargs):

    Model = Pool().get(model_name)
    model = Model()
    values = kwargs.copy()

    for field, value in values.iteritems():
        if field in model._fields:
            if not value:
                continue
            definition = model._fields[field]

            # TODO: avoid functional fields.
            if field in ('vat_code', 'email', 'fax', 'website'):
                continue
            if definition._type in ('one2many', 'many2many'):
                relation = Pool().get(definition['relation'])
                for v in value:
                    if v.id and v.id > 0:
                        v = relation(v.id)
                    getattr(model, field).append(v)
            else:
                setattr(model, field, value)
    return model


def create_party(party_dict):
    return create_model('party.party', **party_dict)


# def party_exists_by_name(name):
#     Party = Pool().get('party.party')
#     parties = Party.search(('name', '=', name), limit=1)
#     if parties:
#         return parties[0]


def party_exists_by_code(code):
    Party = Pool().get('party.party')
    parties = Party.search(('code', '=', code), limit=1)
    if parties:
        return parties[0]


def party_exists_by_identifier(code, type='eu_vat'):
    PartyId = Pool().get('party.identifier')
    parties = PartyId.search(('code', '=', code), ('type', '=', type), limit=1)
    if parties:
        return parties[0].party


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

    values = {}
    values['code'] = vat_code
    values['type'] = 'migration'
    if vat.is_valid(vat_code):
        values['type'] = 'eu_vat'

    return create_model('party.identifier', **values)


def create_identifiers(code, type):
    values = {
        'code': code,
        'type': type
    }
    return create_model('party.identifier', **values)


def create_contact_mechanism(values):
    return create_model('party.contact_mechanism', **values)
