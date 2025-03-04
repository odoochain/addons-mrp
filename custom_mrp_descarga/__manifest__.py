# Copyright 2022 Berezi Amubieta - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Custom MRP Descarga",
    "version": "14.0.1.0.0",
    "category": "MRP",
    "license": "AGPL-3",
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "depends": [
        "custom_mrp_line_cost",
        "custom_descarga",
        "custom_breeding_apps",
        "mrp_production_deconstruction",
        "custom_saca_intercompany",
        "mrp_bom_category",
        "custom_saca_timesheet",
        "stock_move_line_cost",
        "stock_picking_batch_liquidation",
        "stock_picking_cancel",
        "stock_move_in_out_qty"
    ],
    "data": [
        "data/quartering_product.xml",
        "data/ir_sequence.xml",
        "data/mrp_bom_category.xml",
        "views/saca_line_view.xml",
        "views/mrp_production_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_quant_view.xml",
        "views/mrp_bom_view.xml",
        "views/product_template_view.xml",
        "views/stock_move_line_view.xml",
        "views/killing_cost_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}
