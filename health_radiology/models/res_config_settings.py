# -*- coding: utf-8 -*-
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    health_radiology_pacs_server_url = fields.Char(
        string='URL Server DICOM PACS Web Viewer',
        default='https://pacs.hospital.id/viewer?study=',
        help='Prefix URL server PACS eksternal (misal Orthanc, OHIF Viewer, atau Cornerstone)',
        config_parameter='health_radiology.pacs_server_url'
    )

    health_radiology_default_radiologist_id = fields.Many2one(
        'health.physician',
        string='Dokter Spesialis Radiologi (Sp.Rad) Utama',
        config_parameter='health_radiology.default_radiologist_id'
    )
