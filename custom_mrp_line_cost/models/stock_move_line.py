# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _default_pallet_id(self):
        if "default_production_id" in self.env.context:
            result = self.env["mrp.production"].browse(self.env.context.get("default_production_id")).pallet_id.id
        else:
            result = False
        return result

    container = fields.Integer(string="Containers")
    unit = fields.Integer(string="Unit")
    product_unit_container = fields.Integer(
        string="Product Unit/Container",
        related="product_id.unit_container",
        store=True)
    unit_container = fields.Float(
        string="Unit/Container")
    weight = fields.Float(
        string="Weight",
        compute="_compute_weight",
        store=True,
        digits="Killing Cost Decimal Precision")
    percentage = fields.Float(
        string="%",
        compute="_compute_percentage",
        store=True,
        digits="MRP Price Decimal Precision")
    base_price = fields.Float(
        string="Base Price",
        digits="MRP Price Decimal Precision",
        compute="_compute_base_price",
        store=True)
    applied_price = fields.Float(
        string="Applied Price",
        digits="MRP Price Decimal Precision")
    expense_kg = fields.Boolean(
        string="Cost/Kgm",
        compute="_compute_expense_kg",
        store=True)
    canal = fields.Boolean(
        string="Canal",
        related="product_id.canal",
        store=True)
    brut = fields.Float(
        string="Brut")
    pallet = fields.Integer(
        string="Pallet Qty")
    month_cost = fields.Float(
        string="Month Cost",
        compute="_compute_month_cost",
        store=True)
    pallet_id = fields.Many2one(
        string="Pallet",
        comodel_name="product.product",
        default=_default_pallet_id,
        domain="[('palet', '=', True)]")

    @api.depends("production_id", "production_id.date_planned_start",
                 "move_id", "move_id.bom_line_id",
                 "move_id.bom_line_id.operation_id",
                 "move_id.bom_line_id.operation_id.workcenter_id",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.january",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.february",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.march",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.april",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.may",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.june",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.july",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.august",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.september",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.october",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.november",
                 "move_id.bom_line_id.operation_id.workcenter_id.cost_ids.december"
                 )
    def _compute_month_cost(self):
        for line in self:
            month_cost = 0
            if line.production_id.date_planned_start and line.move_id and (
                line.move_id.byproduct_id) and (
                    line.move_id.byproduct_id.operation_id):
                month = line.production_id.date_planned_start.month
                if month == 1:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.january
                if month == 2:
                    month_cost= line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.february
                if month == 3:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.march
                if month == 4:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.april
                if month == 5:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.may
                if month == 6:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.june
                if month == 7:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.july
                if month == 8:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.august
                if month == 9:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.september
                if month == 10:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.october
                if month == 11:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.november
                if month == 12:
                    month_cost = line.move_id.byproduct_id.operation_id.workcenter_id.cost_ids.december
            line.month_cost = month_cost

    @api.depends("move_id", "move_id.bom_line_id", "move_id.byproduct_id",
                 "move_id.bom_line_id.expense_kg",
                 "move_id.byproduct_id.expense_kg")
    def _compute_expense_kg(self):
        for line in self:
            if line.move_id and line.move_id.bom_line_id:
                line.expense_kg = line.move_id.bom_line_id.expense_kg
            if line.move_id and line.move_id.byproduct_id:
                line.expense_kg = line.move_id.byproduct_id.expense_kg

    @api.depends("production_id.purchase_unit_price",
                 "production_id.average_cost",
                 "production_id.month_cost",
                 "production_id.is_deconstruction")
    def _compute_base_price(self):
        for line in self:
            line.base_price = 0
            if line.production_id and not line.production_id.date_planned_start:
                raise ValidationError(
                        _("You must introduce the planned date."))
            else:
                cost = 0
                if line.production_id and (
                    line.move_id.bom_line_id) and (
                        line.production_id.is_deconstruction):
                    cost = line.move_id.bom_line_id.cost
                    if line.expense_kg:
                        cost = (
                            line.production_id.month_cost + (
                                line.production_id.purchase_unit_price)) * (
                                    line.move_id.bom_line_id.coefficient)
                elif line.production_id and line.move_id.byproduct_id:
                    cost = line.move_id.byproduct_id.cost
                    if line.expense_kg:
                        cost = (
                            line.month_cost + (
                                line.production_id.average_cost)) * (
                                    line.move_id.byproduct_id.coefficient)
                line.base_price = cost

    @api.depends("unit", "qty_done")
    def _compute_weight(self):
        for line in self:
            if line.unit != 0:
                line.weight = line.qty_done / line.unit

    @api.depends("qty_done", "production_id", "production_id.origin_qty")
    def _compute_percentage(self):
        for line in self:
            if line.production_id.origin_qty != 0:
                line.percentage = (
                    line.qty_done * 100 / line.production_id.origin_qty)

    @api.onchange("brut", "pallet", "container", "pallet_id")
    def onchange_brut(self):
        if self.brut:
            self.qty_done = self.brut - (
                self.pallet * self.pallet_id.weight) - (
                    self.container * self.production_id.packaging_id.weight)

    @api.onchange("container")
    def onchange_container(self):
        if self.container:
            self.unit = self.product_unit_container * self.container
            self.unit_container = self.product_unit_container

    @api.onchange("unit")
    def onchange_unit(self):
        if self.unit and self.container != 0:
            self.unit_container = self.unit / self.container
        if self.unit and self.product_id and self.product_id.asphyxiated:
            self.qty_done = self.unit * self.production_id.average_weight

    @api.onchange("base_price")
    def onchange_base_price(self):
        self.ensure_one()
        if self.base_price:
            self.applied_price = self.base_price
            self.onchange_applied_price()

    @api.onchange("applied_price")
    def onchange_applied_price(self):
        if self.applied_price:
            self.standard_price = self.applied_price
            self.onchange_standard_price()
