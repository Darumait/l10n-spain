# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Move the stale pre-16.0 ``not_in_mod347`` column out of the way.

Until 15.0 ``res.partner.not_in_mod347`` was a plain stored Boolean. 16.0 made
it ``company_dependent`` (so ``store=False``, values in ``ir_property``), which
left the old boolean column orphaned in the table -- Odoo never drops columns
it no longer recognises. 18.0 stores company-dependent fields as a real
``jsonb`` column, so ``_auto_init`` tries to cast that leftover boolean column
and Postgres refuses with "cannot cast type boolean to jsonb".

Databases that passed through l10n_es_aeat_mod347 16.0.1.11.5 already had this
done by its pre-migration; those jumping straight from an older 16.0 (or from
15.0) to 18.0 never ran it.

The old values are kept in ``old_not_in_mod347`` rather than dropped. They are
frozen as of the 16.0 upgrade -- anything set since then lives in
``ir_property`` and is migrated to jsonb by this version's post-migration.
"""

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        """
        SELECT data_type
          FROM information_schema.columns
         WHERE table_name = 'res_partner'
           AND column_name = 'not_in_mod347'
        """
    )
    row = env.cr.fetchone()
    # Only the leftover pre-16.0 boolean column needs moving. A jsonb column
    # is already the 18.0 layout (e.g. a retried upgrade), so leave it alone.
    if row and row[0] == "boolean":
        openupgrade.rename_columns(
            env.cr, {"res_partner": [("not_in_mod347", "old_not_in_mod347")]}
        )
