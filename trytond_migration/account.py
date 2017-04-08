# -*- coding: utf-8 -*-
# Tryton imports
from trytond.transaction import Transaction
from trytond.pool import Pool
import unicodedata


def migrate_accounts(company, accounts):
    Account = Pool().get('account.account')
    Account.parent.left = None
    Account.parent.right = None

    _upload_accounts(company, accounts)

    Account.parent.left = 'left'
    Account.parent.right = 'right'


def _get_similar_account(code, digits, chart):
    account = None
    if len(code) < digits:
        for digits in (4, 3, 2, 1):
            code2 = code[:digits]
            account = chart.get(code2)
            if account:
                break

    if len(code) == digits:
        # Ensure that we find a valid account
        for i in range(len(code)):
            sub_code = code[:-i].ljust(digits, '0')
            if sub_code in chart:
                new_account = chart.get(sub_code)
                if new_account:
                    new_account2, p = new_account
                if new_account2.kind != 'view':
                    account = new_account
                    break

    if account:
        return account

    acc = '1'.ljust(digits, '0')
    similar = chart.get(acc)
    return similar


def _similar_account(sim_account, code):
    Account = Pool().get('account.account')
    account = Account()
    ignore_fields = ['id', 'code', 'name', 'childs', 'deferrals',
        'taxes', 'create_date', 'create_uid', 'write_date',
        'write_uid', 'template', 'parent', 'company',
        'general_ledger_balance', 'balance', 'credit',
        'debit', 'right', 'left', 'rec_name']

    for field in Account._fields:
        if field in ignore_fields:
            continue
        value = getattr(sim_account, field)
        setattr(account, field, value)

    if (sim_account.code and sim_account.parent and
            len(code) == len(sim_account.code)):
        account.parent = sim_account.parent
    else:
        account.parent = sim_account

    return account


def _upload_accounts(company, accounts_dict):
    pool = Pool()
    Account = pool.get('account.account')
    AccountConfig = pool.get('account.configuration')

    account_config = AccountConfig(1)
    digits = account_config.default_account_code_digits
    chart = get_chart_tree(company)

    unknown = None  # unknown_account_type
    accounts = []
    accounts_sorted = accounts_dict.keys()
    accounts_sorted.sort()
    for element in accounts_sorted:
        account_code = get_code(element, digits)
        account_name = accounts_dict[element]
        if account_code in chart:
            continue

        similar = None, False
        similar = _get_similar_account(account_code, digits, chart)
        similar2, party_required = similar
        account = _similar_account(similar2, account_code)
        account.code = account_code
        account.name = account_name
        if len(account_code) == digits and account.kind == 'view':
            account.kind = 'other'

        chart[account.code] = (account, party_required)
        account.type = account.type if account.type else unknown

        print account.code, account.kind, account.type
        accounts.append(account)

    for i in range(1, int(digits)+1):
        accs = [x for x in accounts if len(x.code) == i]
        Account.save(accs)


def update_parent_left_right():
    """
    Compute left/right fields for a parent field in a tryton table
    """
    def _parent_store_compute(cr, table, field):
        def browse_rec(root, pos=0):
            where = field + '=' + str(root)

            if not root:
                where = field + 'IS NULL'

            cr.execute('SELECT id FROM %s WHERE %s \
                ORDER BY %s' % (table, where, field))
            pos2 = pos + 1
            childs = cr.fetchall()
            for id in childs:
                pos2 = browse_rec(id[0], pos2)
            cr.execute('update %s set "left"=%s, "right"=%s\
                where id=%s' % (table, pos, pos2, root))
            return pos2 + 1

        query = 'SELECT id FROM %s WHERE %s IS NULL order by %s' % (
            table, field, field)
        pos = 0
        cr.execute(query)
        for (root,) in cr.fetchall():
            pos = browse_rec(root, pos)
        return True

    _parent_store_compute(Transaction().connection.cursor(), 'account_account',
        'parent')


def party_codes():
    return ('430', '400', '410', '572')  # Accounts to avoid


def get_code(code, digits):
    if len(code) > 4:
        if code[:3] in party_codes():
            code = code[0:4].ljust(len(code), '0')
    if len(code) > digits:
        i = (digits-4)
        code = code[0:4] + code[-3:]  # TODO
    return code


def get_chart_tree(company):
    Account = Pool().get('account.account')
    accounts = Account.search([('company', '=', company)])
    return dict((str(a.code), (a, a.party_required)) for a in accounts)


def unaccent(text):
    if isinstance(text, str):
        text = unicode(text, 'utf-8')
    elif isinstance(text, unicode):
        pass
    else:
        return str(text)
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore')
