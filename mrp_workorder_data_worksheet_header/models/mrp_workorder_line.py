# Copyright 2021 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, models
from base64 import b64decode, b64encode
from io import BytesIO
from logging import getLogger

logger = getLogger(__name__)

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import PyPDF2")


class MrpWorkorderLine(models.Model):
    _inherit = "mrp.workorder.line"

    def print_report(self):
        records = self.filtered(lambda r: r.finished_workorder_id.worksheet)
        if not records:
            return
        pdf = PdfFileWriter()
        for record in records:
            content, content_type = self.env.ref(
                "mrp_workorder_data_worksheet_header."
                "mrp_workorder_line_worksheet_report"
            ).render_qweb_pdf(res_ids=record.id)

            content_pdf = PdfFileReader(BytesIO(content))
            pdf_worksheet = PdfFileReader(
                BytesIO(b64decode(record.finished_workorder_id.worksheet)),
                strict=False)

            for page in pdf_worksheet.pages:
                new_page = pdf.addBlankPage(
                    page.mediaBox.getWidth(), page.mediaBox.getHeight(),
                )
                new_page.mergePage(content_pdf.getPage(0))
                page.scaleBy(0.95)
                new_page.mergePage(page)

        pdf_content = BytesIO()
        pdf.write(pdf_content)
        pdf_data = pdf_content.getvalue()
        pdf_encoded = b64encode(pdf_data)
        return pdf_encoded

    def get_worksheets(self):
        pdf = self.print_report()
        if not pdf or not self.env.context.get("print", False):
            return self.filtered("finished_workorder_id.worksheet").mapped(
                "finished_workorder_id.worksheet")
        return pdf

    def show_worksheets(self):
        self.ensure_one()
        worksheets = self.get_worksheets()
        if not worksheets:
            return
        wizard = self.env["binary.container"].create({
            "binary_field": (
                worksheets[0] if isinstance(worksheets, list) else worksheets),
        })
        action = self.env.ref("pdf_previewer.binary_container_action")
        action_dict = action and action.read()[0] or {}
        action_dict.update({
            "name": _("Worksheets"),
            "res_id": wizard.id,
        })
        return action_dict
