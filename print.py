import frappe
import pydocusign
import hashlib
import os
import uuid
from frappe.utils.pdf import get_pdf
# from PyPDF2 import PdfFileReader, PdfFileWrite

@frappe.whitelist()
def get_print_settings_to_show(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    print_settings = frappe.get_single("Print Settings")

    if hasattr(doc, "get_print_settings"):
        fields = doc.get_print_settings() or []
    else:
        return []

    print_settings_fields = []
    for fieldname in fields:
        df = print_settings.meta.get_field(fieldname)
        if not df:
            continue
        df.default = print_settings.get(fieldname)
        print_settings_fields.append(df)

    return print_settings_fields

# @frappe.whitelist()
# def get_attachment(doctype, docname):
#     attachments = frappe.get_all('File', filters={
#         'attached_to_name': docname,
#         'attached_to_doctype': doctype,
#     }, fields=['name', 'file_url', 'file_name'])

#     if attachments:
#         return attachments[0]

#     return Noneh

@frappe.whitelist()
def send_purchase_order_to_docusign(doctype, docname):
    try:
        pdf_data = frappe.get_print(doctype, docname)
        # pdf_data = pdf_data.encode("utf-8")

        # Get the attachment from the document
        # attachment = get_attachment(doctype, docname)

        # if not attachment:
        #     frappe.msgprint("Attachment not found.")
        #     return

        # Initialize the DocuSign client
        client = pydocusign.DocuSignClient(
            root_url="https://demo.docusign.net/restapi/v2",
            username="vigneshwebdevelopr@gmail.com",
            password="nacl@123",
            integrator_key="53be8fd1-748e-4bc7-9d72-5c971a20478f",
        )
		

        # Prepare signers
        signers = [
            pydocusign.Signer(
                email='vigneshwebdevelopr@gmail.com',
                name='vignesh',
                recipientId=1,
                clientUserId=str(uuid.uuid4()),  # Unique identifier
                tabs=[
                    pydocusign.SignHereTab(
                        documentId=1,
                        pageNumber=1,
                        xPosition=100,
                        yPosition=100,
                    ),
                ],
                emailSubject="Sign this Purchase Order",
                emailBody="Please sign this Purchase Order.",
                supportedLanguage="en",
            ),
        ]

        # Create an envelope with the selected attachment
        envelope = pydocusign.Envelope(
            documents=[
                pydocusign.Document(
                    name= f"{docname}.pdf",
                    # data= io.BytesIO(pdf_data),
                    ##above code mention the path of the attachement
                )
            ],
            emailSubject="Sign this Purchase Order",
            emailBlurb="Please review and sign this Purchase Order.",
            status=pydocusign.Envelope.STATUS_SENT,
            recipients=signers,
        )

        # Send the envelope for digital signature
        client.create_envelope_from_documents(envelope)

        # Retrieve the signing URL
        signing_url = envelope.post_recipient_view(envelope.recipients[0], returnUrl="http://127.0.0.1:8000/")

        # Update the purchase order status or perform any necessary actions
        # ...

        frappe.msgprint("Purchase Order sent for digital signature. Sign here: {0}".format(signing_url))

        # List signature documents
        document_list = envelope.get_document_list()

        # Download signed documents
        download_path = "path/to/downloaded/documents"  
        os.makedirs(download_path, exist_ok=True)
        for signed_document in document_list:
            document = envelope.get_document(signed_document['documentId'])
            document_path = os.path.join(download_path, signed_document['name'])
            with open(document_path, 'wb') as f:
                f.write(document.read())

        # Download signature certificate
        certificate_path = os.path.join(download_path, "certificate.pdf")
        certificate_document = envelope.get_certificate()
        with open(certificate_path, 'wb') as f:
            f.write(certificate_document.read())

        frappe.msgprint("Signed documents downloaded to {0}".format(download_path))


    except Exception as e:
        frappe.msgprint(f"Error: {str(e)}")
