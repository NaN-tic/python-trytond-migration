from trytond.pool import Pool


def get_user(user_name):
    User = Pool().get('res.user')
    user = User.search([('login', '=', user_name)], limit=1)
    if user:
        return user[0]


def change_company(user, company_id):
    Company = Pool().get('company.company')
    user.company = Company.search([('id', '=', company_id)], limit=1)[0]
    user.main_company = user.company
    user.save()
