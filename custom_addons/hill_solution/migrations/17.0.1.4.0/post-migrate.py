"""Backfill hill.document records for reports saved before the e-sign
feature was introduced.

Creates one unsigned hill.document per saved visit report
(site.report.is_report_saved) and per saved study report
(hill.study.study_report_saved), linking the original saved PDF
attachment when available.
"""


def migrate(cr, version):
    # Visit reports: pick the most recent saved attachment for each report.
    cr.execute(
        """
        INSERT INTO hill_document
            (doc_type, site_report_id, case_id, case_number,
             original_attachment_id, state, create_uid, create_date,
             write_uid, write_date)
        SELECT 'visit', sr.id, sr.case_id, hc.case_number,
               hsd.attachment_id, 'unsigned', 1, now(), 1, now()
        FROM site_report sr
        JOIN hill_case hc ON hc.id = sr.case_id
        JOIN (
            SELECT site_report_id,
                   MAX(uploaded_at) AS last_uploaded
            FROM hill_site_document
            WHERE site_report_id IS NOT NULL
            GROUP BY site_report_id
        ) last_doc ON last_doc.site_report_id = sr.id
        JOIN hill_site_document hsd
          ON hsd.site_report_id = sr.id
         AND hsd.uploaded_at = last_doc.last_uploaded
        WHERE sr.is_report_saved = true
          AND NOT EXISTS (
              SELECT 1 FROM hill_document hd
              WHERE hd.doc_type = 'visit'
                AND hd.site_report_id = sr.id
          )
        """
    )

    # Study reports: pick the most recent saved attachment for each study.
    cr.execute(
        """
        INSERT INTO hill_document
            (doc_type, study_id, case_id, case_number,
             original_attachment_id, state, create_uid, create_date,
             write_uid, write_date)
        SELECT 'study', hs.id, hs.case_id, hc.case_number,
               hsd.attachment_id, 'unsigned', 1, now(), 1, now()
        FROM hill_study hs
        JOIN hill_case hc ON hc.id = hs.case_id
        JOIN (
            SELECT study_id,
                   MAX(uploaded_at) AS last_uploaded
            FROM hill_site_document
            WHERE study_id IS NOT NULL
            GROUP BY study_id
        ) last_doc ON last_doc.study_id = hs.id
        JOIN hill_site_document hsd
          ON hsd.study_id = hs.id
         AND hsd.uploaded_at = last_doc.last_uploaded
        WHERE hs.study_report_saved = true
          AND NOT EXISTS (
              SELECT 1 FROM hill_document hd
              WHERE hd.doc_type = 'study'
                AND hd.study_id = hs.id
          )
        """
    )
