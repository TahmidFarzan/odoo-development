from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResGroups(models.Model):
    _inherit = 'res.groups'
    _description = 'Group for hospital management system'
    
    confirmed_user_id = fields.Many2one('res.users',string="Confirmed user")
    
    def get_application_groups(self,domain):
        group_id = self.env.ref('account.group_warning_account').id
        return super(ResGroups,self).get_application_groups(domain + [('id','!=',group_id)])

