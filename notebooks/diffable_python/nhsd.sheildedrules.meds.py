# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# The Chief Medical Officer has created two groups for different social distancing and shieling
# - “At Risk” – large group (circa 19 million) normally at risk from the flu - should practice strict social distancing
# - “At high risk” – a smaller sub-group (circa 1.5 million), defined by CMO – should practice complete social “shielding”
#
# The "at risk" is basically the flu register and NHS Digital have published their [methodology for high risk shielded patient list identification](https://digital.nhs.uk/coronavirus/shielded-patient-list/methodology). They provided the list as [BNF codes](https://ebmdatalab.net/prescribing-data-bnf-codes/) and following notebook generates codes compliant with the [NHS Dictionary of Medicines and Devices](https://ebmdatalab.net/what-is-the-dmd-the-nhs-dictionary-of-medicines-and-devices/) which is the local UK Snomed drug extension. This is the pure code list - logic needs to be applied which is detailed in the guidance.

from ebmdatalab import bq
import os
import pandas as pd

# +
## The following is written based on version 1 frm March 27th and 
## is archived at https://web.archive.org/save/https://digital.nhs.uk/coronavirus/shielded-patient-list/methodology/medicines-data

sql = '''
WITH bnf_codes AS (  
  SELECT bnf_code FROM hscic.presentation WHERE 
  ##transplant
  bnf_code LIKE '0802%' OR # the following meds are listed in definition but annex looks like they included all meds in this section
  ##respiratory
  bnf_code LIKE '030302%' OR #BNF leukotriene antagonists
  bnf_code LIKE '0603020T0%' OR #BNF prednisolone
  bnf_code LIKE '030101%' OR #BNF adrenoceptor aganosts
  bnf_code LIKE '0302%' OR #BNF corticosteroids resp
  bnf_code LIKE '0303030B0%' OR #BNF roflumilast 
  bnf_code LIKE '030102%' #BNF antimuscarinin brochodilators
   )
SELECT "vmp" AS type, id, bnf_code, nm
FROM dmd.vmp
WHERE bnf_code IN (SELECT * FROM bnf_codes)

UNION ALL

SELECT "amp" AS type, id, bnf_code, descr
FROM dmd.amp
WHERE bnf_code IN (SELECT * FROM bnf_codes)

ORDER BY bnf_code, type, id'''

nhsd_shieldedrules_meds = bq.cached_read(sql, csv_path=os.path.join('..','data','nhsd_shieldedrules_meds .csv'))
pd.set_option('display.max_rows', None)
nhsd_shieldedrules_meds
# -


