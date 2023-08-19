{
    'version' : '1.2',
    'category': 'Hospital',
    
    'name' : 'Hospital management system',
    'author' : 'Seikh Md Tahmid Farzan',
    'summary': 'Learning odoo development',
    'description': "Learning odoo development",
    'website': 'https://www.facebook.com/tahmid.farzan007/',
    
    'depends': ['mail','account','product','sale','sale_stock'],
    
    'data':[
        "security/ir.model.access.csv",
        
        "data/hms.tag.csv",
        "data/sequence.xml",
        "data/tags_data.xml",
        "data/mail_template_data.xml",
        
        "wizard/cancel_appointment_view.xml",
        
        "views/menu.xml",
        "views/patient.xml",
        "views/doctor.xml",
        "views/doctor_male.xml",
        "views/doctor_female.xml",
        "views/doctor_other.xml",
        "views/tag.xml",
        "views/sale_order.xml",
        "views/account_move.xml",
        "views/appointment.xml",
        "views/config_settings_views.xml",
        "views/operation.xml",
        
        'report/patient_details_template.xml',
        'report/patient_card.xml',
        'report/report.xml'
    ],
    
    'demo': [],
    
    'excludes': [],
    
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}