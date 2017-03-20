# -*- coding: utf-8 -*-

from trytond.pool import Pool


def create_model(model_name,  **kwargs):

    Model = Pool().get(model_name)
    model = Model(**kwargs)
    return model
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
