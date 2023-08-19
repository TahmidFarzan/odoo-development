from odoo import _
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HMSDoctor(models.Model):
    _name = 'hms.doctor'
    _description = 'Doctor for hospital management system'
    
    _inherit = ['mail.thread','mail.activity.mixin']
    
    _rec_name = 'reference'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    capitalize_name = fields.Char(string='Capitalize name', tracking=True, compute="_compute_capitalize_name", store=True)
    age = fields.Integer(string='Age', required=True, default="0", tracking=True)
    gender = fields.Selection([("male","Male"),("female","Female"),("other","Other")], string='Gender', required=True, tracking=True)
    note = fields.Text(string='Note', required=False, tracking=True)
    reference = fields.Char(string='Reference', default=lambda self : _("New"))
    active =  fields.Boolean(default=True)
    
    def name_get(self):
        res = []
        for row in self:
            name = f'{row.reference} - {row.name}'
            res.append((row.id,name))
        return res
    
    @api.model_create_multi
    def create(self, vals):
        for row in vals:
            row['reference'] = self.env['ir.sequence'].next_by_code('hms.doctor.reference')
        return super(HMSDoctor, self).create(vals)
    
    @api.constrains('age')
    def _constrains_age(self):
        for row in self:
            if row.age == 0:
                raise ValidationError(_("Age can not less 0. (Age: %s)", row.age))
    
    @api.depends("name")
    def _compute_capitalize_name(self):
        if self.name:
            self.capitalize_name = self.name.upper()
        else:
            self.capitalize_name = self.name