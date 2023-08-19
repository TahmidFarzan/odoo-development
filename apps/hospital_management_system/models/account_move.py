from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    so_confirmed_user_id = fields.Many2one('res.users',string="So Confirmed user")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    line_number = fields.Integer(string="Line number")