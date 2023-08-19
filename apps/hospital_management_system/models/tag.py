from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HMSTag(models.Model):
    _name = 'hms.tag'
    _description = 'Tag for hospital management system'
    
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True,trim=True)
    capitalize_name = fields.Char(string='Capitalize name',  compute="_compute_capitalize_name")
    note = fields.Text(string='Note', required=False, tracking=True)
    active =  fields.Boolean(default=True, copy=False)
    color = fields.Integer(string='Color', required=False, tracking=True)
    color_two = fields.Char(string='Color two', required=False, tracking=True)
    
    def copy(self, default=None):
        if default is None:
            default= {}
        if not default.get('name'):   
            default["name"] = self.name + "(copy)"
        return super(HMSTag,self).copy(default)
    
    @api.depends("name")
    def _compute_capitalize_name(self):
        if self.name:
            self.capitalize_name = self.name.upper()
        else:
            self.capitalize_name = self.name
            
    _sql_constraints =[
        # ('Name','constraints(Field)','Message')
        # ('Name','constraints(Field1,Field2,...)','Message')
        ('unique_name','unique(name)','Name must be unique.')
    ]
    