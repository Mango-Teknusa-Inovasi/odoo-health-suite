# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json

class HealthQueueDisplayController(http.Controller):

    @http.route('/health/queue/display', type='http', auth='public', website=False)
    def queue_display_screen(self, **kwargs):
        """Fullscreen TV digital display screen for polyclinic waiting lounge."""
        today = fields.Date.context_today(request.env.user)
        departments = request.env['health.department'].sudo().search([('type', '=', 'outpatient')])
        company = request.env.company

        # Active queue appointments
        calling = request.env['health.appointment'].sudo().search([
            ('appointment_date', '=', today),
            ('state', '=', 'in_consultation')
        ], order='write_date desc', limit=4)

        waiting = request.env['health.appointment'].sudo().search([
            ('appointment_date', '=', today),
            ('state', '=', 'waiting')
        ], order='queue_number asc', limit=8)

        values = {
            'company': company,
            'departments': departments,
            'calling_appointments': calling,
            'waiting_appointments': waiting,
            'today': today,
        }
        return request.render('health_appointment.queue_display_tv_template', values)

    @http.route('/health/queue/api/live', type='json', auth='public')
    def queue_live_data(self, **kwargs):
        """JSON endpoint polled by display TV for real-time queue refresh."""
        today = fields.Date.context_today(request.env.user)
        calling = request.env['health.appointment'].sudo().search([
            ('appointment_date', '=', today),
            ('state', '=', 'in_consultation')
        ], order='write_date desc', limit=4)

        waiting = request.env['health.appointment'].sudo().search([
            ('appointment_date', '=', today),
            ('state', '=', 'waiting')
        ], order='queue_number asc', limit=10)

        return {
            'calling': [{
                'id': a.id,
                'queue_number': a.queue_number,
                'patient_name': a.patient_id.name,
                'department_name': a.department_id.name,
                'physician_name': a.physician_id.name,
            } for a in calling],
            'waiting': [{
                'id': w.id,
                'queue_number': w.queue_number,
                'department_name': w.department_id.name,
            } for w in waiting],
        }
