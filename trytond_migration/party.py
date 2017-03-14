#-*- coding: utf-8 -*-
import sys
import stdnum.eu.vat as vat

#Tryton imports
from trytond.transaction import Transaction
from trytond.pool import Pool

def create_model(model,  **kwargs):
    model = Pool().get(model)
    values = kwargs.copy()

    for field, value in values.iteritems():
        if field in model._fields:
            if not value:
                continue
            definition = model._fields[field]

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
    return create_model(model='party.party', **party_dict)


def create_address(model, party_dict):
    zips = get_zip(party_dict['zip'])[0]
    if zips and zips != None:
        party_dict.update({'country': zips.country.id,
            'subdivision': zips.subdivision.id})

    return create_model(model='party.address', **party_dict)


def get_zip(zip_code):
    CountryZip = Pool().get('country.zip')
    zip_n = CountryZip()
    zips = zip_n.search([('zip', '=', zip_code)], limit=1)
    if zips != []:
        return zips
    else:
        return None


def create_identifiers(model, values, country='ES'):
    values['vat_code'] = values['vat_code'].upper().strip()
    values['vat_code'] = country + values['vat_code'].replace('-', '')

    values['type'] = 'migration'
    if vat.is_valid(values['vat_code']):
        values['type'] = 'eu_vat'

    return create_model(model='party.identifier', **values)


def create_contact_mechanism(model, party_dict):
    return create_model(model='party.contact_mechanism', **party_dict)
