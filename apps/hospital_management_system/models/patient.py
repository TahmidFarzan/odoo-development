from odoo import _
from datetime import date
from dateutil import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class HMSPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Patient for hospital management system'
    
    _inherit = ['mail.thread','mail.activity.mixin']
    
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    capitalize_name = fields.Char(string='Capitalize name', tracking=True, compute="_compute_capitalize_name", store=True)
    date_of_birth = fields.Date(string='Date of bith', tracking=True)
    age = fields.Integer(string='Age', default="0", store=True ,tracking=True, compute="_compute_age", inverse="_inverse_compute_age", search="_search_age")
    is_child = fields.Boolean(string='Is child?', required=True,  tracking=True)
    gender = fields.Selection([("male","Male"),("female","Female"),("other","Other")], string='Gender', required=True, tracking=True)
    note = fields.Text(string='Note', required=False, tracking=True)
    reference = fields.Char(string='Reference', default=lambda self : _("New"))
    active =  fields.Boolean(default=True)
    image = fields.Image(string='Image', required=False, tracking=True)
    appointment_count = fields.Integer(string='Appointment count', tracking=True, store=True, compute="_compute_appointment_count")
    appointment_ids = fields.One2many('hms.appointment','patient_id',string="Appointments")
    
    parent = fields.Char(string='Parent', tracking=True)
    maritial_status = fields.Selection([("married","Married"),("single","Single"),("engaged","Engaged"),("divorced","Divorced")], string='Maritial status', required=True, tracking=True)
    patner_name = fields.Char(string='Patner name', tracking=True)
    
    is_birthday = fields.Boolean(string='Is birthday', compute="_compute_is_birthday", default=False)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    website = fields.Char(string='Web site', tracking=True)
    
    @api.depends("date_of_birth")
    def _compute_is_birthday(self):
        today = date.today()
        for row in self:
            row.is_birthday = False
            if row.date_of_birth:
                if today.day == row.date_of_birth.day and today.month == row.date_of_birth.month:
                    row.is_birthday = True
    
    @api.depends("appointment_ids")
    def _compute_appointment_count(self):
        #for row in self:
            # count = self.env['hms.appointment'].search_count([('patient_id','=',row.id)])
            #row.appointment_count = count
        appoinment_groups = self.env['hms.appointment'].read_group(domain=['state','!=','cancel'],fields=['patient_id'],groupby=['patient_id'])
        for gp_row in appoinment_groups:
            patient_id = gp_row.get('patient_id')[0]
            patient_rec = self.browse(patient_id)
            patient_rec.appointment_count = gp_row['patient_id_count']
            self = self - patient_rec
        self.appointment_count = 0
    
    def name_get(self):
        res = []
        for row in self:
            name = f'{row.reference} - {row.name}'
            res.append((row.id,name))
        return res
    
    @api.model_create_multi
    def create(self, vals):
        for row in vals:
            row['reference'] = self.env['ir.sequence'].next_by_code('hms.patient.reference')
        return super(HMSPatient, self).create(vals)
    
    @api.constrains('age','is_child')
    def _constrains_age(self):
        for row in self:
            if row.is_child == False and row.age == 0:
                raise ValidationError(_("Adult age can not less then 0. (Age: %s)", row.age))
    
    @api.depends("name")
    def _compute_capitalize_name(self):
        if self.name:
            self.capitalize_name = self.name.upper()
        else:
            self.capitalize_name = self.name
            
    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for row in self:
            if row.date_of_birth:
                row.age = today.year - row.date_of_birth.year
            else:
                row.age = 0
            
    @api.depends('age')     
    def _inverse_compute_age(self):
        today = date.today()
        for row in self:
            row.date_of_birth = today - relativedelta.relativedelta(years=row.age)
    
    @api.onchange('age')
    def _onchange_age(self):
        if self.age < 18:
            self.is_child = True
        else:
            self.is_child = False
            
    @api.ondelete(at_uninstall = False)
    def _check_appoinment(self):
        for row in self:
            if row.appointment_ids:
                raise ValidationError(_("Can not delete patient with appoinment."))
    
    def _search_age(self,operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(years=value)
        
        start_of_year = date_of_birth.replace(day=1,month=1)
        date_of_birth = date_of_birth.replace(day=31,month=12)
        return [('date_of_birth', '>=', start_of_year),('date_of_birth', '<=', date_of_birth)]
            
    def test_action(self):
        return {
            'type' :  'ir.actions.act_url',
            'target' :  'new',
            'url'    : 'https://www.facebook.com/tahmid.farzan007/',
        }
    
    def action_view_appointments(self):
        return {
            'name' : _( 'Appoinment'),
            'res_model' :  'hms.appointment',
            'view_mode' :  'tree,form,activity,calendar',
            'context' :  {'default_patient_id' : self.id},
            'domain' :  [('patient_id','=',self.id)],
            'target' :  'current',
            'type' :  'ir.actions.act_window',
        }