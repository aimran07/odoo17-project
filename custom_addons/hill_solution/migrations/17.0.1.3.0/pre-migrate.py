"""Pre-migrate hill.service.type.

Convert the legacy Selection (varchar) service_type columns on
hill.case, site.report and hill.invoice.line to Many2one ids before
Odoo alters the columns to int4. This script is idempotent so it can
safely re-run if a previous upgrade attempt aborted mid-way.
"""

SEEDS = [
    # (code, name, client_type, sequence)
    ('ndd_heat_destratifier', 'NDD Heat destratifier', 'b2b', 10),
    ('led_study', 'LED study', 'b2b', 20),
    ('study_163', 'Study 163', 'b2b', 30),
    ('regulatory_audit', 'Regulatory audit', 'b2b', 40),
    ('sizing_171', 'Sizing 171', 'b2c', 10),
    ('study_174', 'Study 174', 'b2c', 20),
    ('study_175', 'Study 175', 'b2c', 30),
    ('study_179', 'Study 179', 'b2c', 40),
]

# Tables whose service_type column changed from Selection (varchar) to
# Many2one (int4).
SERVICE_TYPE_TABLES = ('hill_case', 'site_report', 'hill_invoice_line')


def _column_is_varchar(cr, table):
    """Return True when table.service_type is still a character column."""
    cr.execute(
        """
        SELECT data_type
        FROM information_schema.columns
        WHERE table_name = %s AND column_name = 'service_type'
        """,
        (table,),
    )
    row = cr.fetchone()
    return bool(row and row[0] in ('character varying', 'character', 'text'))


def migrate(cr, version):
    cr.execute("""
        CREATE TABLE IF NOT EXISTS hill_service_type (
            id serial NOT NULL,
            name varchar,
            code varchar,
            client_type varchar,
            sequence integer,
            active boolean,
            create_uid integer,
            create_date timestamp,
            write_uid integer,
            write_date timestamp,
            PRIMARY KEY (id)
        )
    """)

    for code, name, client_type, sequence in SEEDS:
        cr.execute(
            """
            SELECT id FROM hill_service_type WHERE code = %s
            """,
            (code,),
        )
        row = cr.fetchone()
        if row:
            service_id = row[0]
        else:
            cr.execute(
                """
                INSERT INTO hill_service_type
                    (name, code, client_type, sequence, active,
                     create_uid, create_date, write_uid, write_date)
                VALUES (%s, %s, %s, %s, true, 1, now(), 1, now())
                RETURNING id
                """,
                (name, code, client_type, sequence),
            )
            service_id = cr.fetchone()[0]

        cr.execute(
            """
            SELECT id FROM ir_model_data
            WHERE module = 'hill_solution' AND name = %s
            """,
            ('service_type_%s' % code,),
        )
        if not cr.fetchone():
            cr.execute(
                """
                INSERT INTO ir_model_data
                    (create_date, write_date, create_uid, write_uid,
                     module, name, model, res_id, noupdate)
                VALUES (now(), now(), 1, 1, 'hill_solution', %s,
                        'hill.service.type', %s, true)
                """,
                ('service_type_%s' % code, service_id),
            )

    for table in SERVICE_TYPE_TABLES:
        # Only convert while the column is still a character column. Once
        # Odoo has altered it to int4 the data is already mapped, and
        # comparing an integer column against the text codes would raise
        # "operator does not exist: integer = character varying".
        if not _column_is_varchar(cr, table):
            continue
        cr.execute(
            """
            UPDATE %s AS t
            SET service_type = s.id
            FROM hill_service_type AS s
            WHERE t.service_type = s.code
            """ % table,
        )
        cr.execute(
            """
            UPDATE %s
            SET service_type = NULL
            WHERE service_type IS NOT NULL
              AND service_type !~ '^[0-9]+$'
            """ % table,
        )

    # Remove the stale ir.model.fields.selection records that remain from
    # the old Selection fields. When the module load finishes, Odoo's
    # _process_end would otherwise unlink them, which triggers
    # _process_ondelete reading field.ondelete of the new Many2one field
    # (a string) and crashes with
    # "AttributeError: 'str' object has no attribute 'get'".
    cr.execute(
        """
        SELECT s.id
        FROM ir_model_fields_selection s
        JOIN ir_model_fields f ON s.field_id = f.id
        WHERE f.name = 'service_type'
          AND f.model IN ('hill.case', 'site.report', 'hill.invoice.line')
        """
    )
    selection_ids = [row[0] for row in cr.fetchall()]
    if selection_ids:
        cr.execute(
            """
            DELETE FROM ir_model_data
            WHERE model = 'ir.model.fields.selection'
              AND module = 'hill_solution'
              AND res_id = ANY(%s)
            """,
            (selection_ids,),
        )
        cr.execute(
            """
            DELETE FROM ir_model_fields_selection
            WHERE id = ANY(%s)
            """,
            (selection_ids,),
        )
