import json
import re
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import get_url
from frappe.utils.pdf import get_pdf


def _parse_recipients(value):
    if not value:
        return []

    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed if str(v).strip()]
        except Exception:
            pass
        return [v.strip() for v in value.split(',') if v.strip()]

    return []


def _clean_phone(phone):
    if not phone:
        return ''
    return re.sub(r'\D', '', str(phone))


def _get_invoice(invoice_name):
    if not invoice_name:
        frappe.throw(_('Invoice name is required'))

    doc = frappe.get_doc('Sales Invoice', invoice_name)
    if not doc.has_permission('read'):
        frappe.throw(_('Not permitted'), frappe.PermissionError)
    return doc


def _get_contact_email(doc):
    return (
        getattr(doc, 'contact_email', None)
        or frappe.db.get_value('Customer', doc.customer, 'email_id')
        or None
    )


def _get_contact_mobile(doc):
    return (
        getattr(doc, 'contact_mobile', None)
        or frappe.db.get_value('Customer', doc.customer, 'mobile_no')
        or None
    )


def _get_default_print_format():
    return (
        frappe.get_meta('Sales Invoice').default_print_format
        or frappe.db.get_value(
            'Property Setter',
            {'doc_type': 'Sales Invoice', 'property': 'default_print_format'},
            'value',
        )
        or 'Standard'
    )


def _invoice_pdf_content(doc, print_format=None, letterhead=1):
    print_format = print_format or _get_default_print_format()
    html = frappe.get_print(
        'Sales Invoice',
        doc.name,
        print_format=print_format,
        doc=doc,
        no_letterhead=0 if int(letterhead or 0) else 1,
    )
    return get_pdf(html)


def _get_or_create_public_pdf(doc, print_format=None, letterhead=1):
    """Create a public File record and return its absolute URL.

    WhatsApp click-to-chat cannot attach a PDF directly, so POSNext shares a
    public link to the generated invoice PDF.
    """
    content = _invoice_pdf_content(doc, print_format=print_format, letterhead=letterhead)
    file_name = f'{doc.name}.pdf'

    file_doc = frappe.get_doc({
        'doctype': 'File',
        'file_name': file_name,
        'attached_to_doctype': 'Sales Invoice',
        'attached_to_name': doc.name,
        'content': content,
        'is_private': 0,
    })
    file_doc.save(ignore_permissions=True)
    return get_url(file_doc.file_url)


@frappe.whitelist()
def send_invoice_email(invoice_name, recipients=None, subject=None, message=None, print_format=None, letterhead=1):
    """Send Sales Invoice by email with the PDF attached."""
    doc = _get_invoice(invoice_name)
    recipients = _parse_recipients(recipients)

    if not recipients:
        email = _get_contact_email(doc)
        if email:
            recipients = [email]

    if not recipients:
        frappe.throw(_('Please enter an email address.'))

    print_format = print_format or _get_default_print_format()
    subject = subject or _('Invoice {0}').format(doc.name)
    message = message or _('Please find attached your invoice {0}.').format(doc.name)

    attachments = [
        frappe.attach_print(
            'Sales Invoice',
            doc.name,
            file_name=doc.name,
            print_format=print_format,
            print_letterhead=bool(int(letterhead or 0)),
        )
    ]

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        attachments=attachments,
        reference_doctype='Sales Invoice',
        reference_name=doc.name,
        now=False,
    )

    return {
        'success': True,
        'message': _('Email queued successfully.'),
        'recipients': recipients,
    }


@frappe.whitelist()
def get_invoice_whatsapp_share(invoice_name, phone=None, message=None, print_format=None, letterhead=1):
    """Return a WhatsApp URL with a generated public PDF invoice link."""
    doc = _get_invoice(invoice_name)
    pdf_url = _get_or_create_public_pdf(doc, print_format=print_format, letterhead=letterhead)
    phone = _clean_phone(phone or _get_contact_mobile(doc))

    company = doc.company or frappe.defaults.get_global_default('company') or ''
    text = message or _('Hello, here is your invoice {0} from {1}: {2}').format(
        doc.name,
        company,
        pdf_url,
    )

    if phone:
        whatsapp_url = f'https://wa.me/{phone}?text={quote(text)}'
    else:
        whatsapp_url = f'https://wa.me/?text={quote(text)}'

    return {
        'success': True,
        'invoice': doc.name,
        'phone': phone,
        'pdf_url': pdf_url,
        'message': text,
        'whatsapp_url': whatsapp_url,
    }
