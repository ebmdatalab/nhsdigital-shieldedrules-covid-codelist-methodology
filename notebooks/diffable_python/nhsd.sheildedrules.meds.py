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
  (##transplant
  bnf_code LIKE '0802%' OR # the following meds are listed in definition but annex looks like they included all meds in this section
  ##respiratory
  bnf_code LIKE '030302%' OR #BNF leukotriene antagonists
  bnf_code LIKE '0603020T0%' OR #BNF prednisolone
  bnf_code LIKE '030101%' OR #BNF adrenoceptor aganosts
  bnf_code LIKE '0302%' OR #BNF corticosteroids resp
  bnf_code LIKE '0303030B0%' OR #BNF roflumilast 
  bnf_code LIKE '030102%') #BNF antimuscarinin brochodilators
  AND
  (bnf_code NOT LIKE '0802020T0%XAX' OR #BNF tacrolimus mouthwash
  bnf_code NOT LIKE '0301011R0%')
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
nhsd_shieldedrules_meds.head(10)
# -

# The [CMO guidance on "at risk"](https://www.gov.uk/government/publications/guidance-on-shielding-and-protecting-extremely-vulnerable-persons-from-covid-19/guidance-on-shielding-and-protecting-extremely-vulnerable-persons-from-covid-19) is defined as
#
# 1. Solid organ transplant recipients.
# 2. People with specific cancers:
#   - people with cancer who are undergoing active chemotherapy or radical radiotherapy for lung cancer
#   - people with cancers of the blood or bone marrow such as leukaemia, lymphoma or myeloma who are at any stage of treatment
#   - people having immunotherapy or other continuing antibody treatments for cancer
#   - people having other targeted cancer treatments which can affect the immune system, such as protein kinase inhibitors or PARP inhibitors
#   - people who have had bone marrow or stem cell transplants in the last 6 months, or who are still taking immunosuppression drugs
#   - People with severe respiratory conditions including all cystic fibrosis, severe asthma and severe COPD.
# 3. People with rare diseases and inborn errors of metabolism that significantly increase the risk of infections (such as SCID, homozygous sickle cell).
# 4. People on immunosuppression therapies sufficient to significantly increase risk of infection.
# 5. Women who are pregnant with significant heart disease, congenital or acquired.

# The NHS Digital medicines supports identification of transplant recipients (it might not identify all these patients as in some places osp supplies direct), sever asthma/COPD but medicines could be used on all other points with additional clinical codes. Some ideas
# - Pregancy related code plus prescription of medicines related to heart disease ([see GitHub repo](https://github.com/ebmdatalab/cvd-covid-codelist-notebook))
# - Cystic Fibrosis code or [prescription of colistin](https://openprescribing.net/analyse/#org=CCG&numIds=0501070I0&denom=nothing&selectedTab=summary) (in some areas this is supplied via shared care)
# - immnuosuppression plus increased risk of infection ([see BSRM guidance](https://www.rheumatology.org.uk/Portals/0/Documents/Rheumatology_advice_coronavirus_immunosuppressed_patients_220320.pdf?ver=2020-03-23-165636-767))
