**MIDTERM PROJECT INSTRUCTIONS**

**Primary Geospatial Data Collection and Dataset Preparation**

| **Course**            | CPE15: Professional Elective 1 — Programming for Data Science          |
|-----------------------|------------------------------------------------------------------------|
| **Project**           | Part I: Field Data Collection, Validation, Cleaning, and Documentation |
| **Study Area**        | Poblacion, Lucban, Quezon                                              |
| **Assessment Period** | Midterm                                                                |

> **Important:** The objective is to produce a defensible primary dataset. The quality of the Midterm output will determine whether the dataset is accepted for use in the Final Project. Completeness, traceability, consistency, and field verification are more important than simply collecting a large number of records.

# 1. Project Purpose

Each group will build an original point dataset of establishments within an assigned portion of Poblacion, Lucban, Quezon using the SW Maps mobile application. Students will experience the research data pipeline from field observation to a clean, documented, analysis ready dataset.

This project treats each establishment record as a research observation. Every submitted feature must therefore be traceable to an actual field visit or direct field verification.

# 2. Expected Learning Outcomes

**1.** Design and implement a consistent field data collection protocol using a mobile GIS application.

**2.** Capture geographic coordinates and structured attributes using a standardized schema.

**3.** Apply data quality control procedures to identify duplicate, incomplete, inconsistent, or invalid records.

**4.** Use Python and pandas to clean, standardize, validate, and document a real world dataset.

**5.** Prepare a reusable dataset with sufficient provenance for later statistical and geospatial analysis.

# 3. Study Area and Sampling Coverage

The class will divide Poblacion, Lucban into assigned survey areas. Each group is responsible for systematic coverage of its assigned area. Groups should avoid selective collection based only on convenient or well known establishments.

- Survey the assigned area systematically, street by street or block by block.

- Record establishments that are physically observable during the survey.

- Do not intentionally omit small establishments when they satisfy the project inclusion criteria.

- Avoid collecting the same establishment more than once unless the records clearly represent separate branches or locations.

- Document areas that could not be surveyed and state the reason in the field report.

# 4. Inclusion and Exclusion Criteria

## 4.1 Include

Commercial, service, institutional, tourism, accommodation, food, retail, financial, health, and other publicly identifiable establishments located within the assigned survey area.

## 4.2 Exclude

- Private residences with no publicly identifiable establishment function.

- Temporary observations that cannot be reasonably verified as an establishment.

- Sensitive personal information unrelated to the establishment.

- Features outside the assigned survey area unless specifically authorized by the instructor.

# 5. Standard Attribute Schema

| **Field**            | **Type** | **Definition**                           | **Example**            | **Rule**     |
|----------------------|----------|------------------------------------------|------------------------|--------------|
| feature_id           | Text     | Unique record identifier                 | LUC_G03_001            | Required     |
| name                 | Text     | Official or displayed establishment name | Cafe Example           | Required     |
| category             | Text     | Standard major classification            | Food and Dining        | Required     |
| subcategory          | Text     | Specific establishment type              | Cafe                   | Required     |
| street               | Text     | Street or road name                      | Quezon Avenue          | Required     |
| barangay             | Text     | Barangay or local area                   | Poblacion              | Required     |
| latitude             | Decimal  | GPS latitude                             | 14.113245              | Required     |
| longitude            | Decimal  | GPS longitude                            | 121.555231             | Required     |
| location_description | Text     | Landmark or additional location note     | Near municipal hall    | Recommended  |
| operating_status     | Text     | Observed operating state                 | Open                   | Required     |
| opening_hours        | Text     | Publicly displayed operating hours       | 8:00 AM to 8:00 PM     | If available |
| contact_info         | Text     | Public business contact only             | Publicly posted number | If available |
| date_collected       | Date     | Field observation date                   | YYYY-MM-DD             | Required     |
| collector            | Text     | Group or collector identifier            | Group 03               | Required     |
| remarks              | Text     | Relevant field note                      | Second floor           | Optional     |
| verified             | Text     | Field validation status                  | Yes                    | Required     |

# 6. Standard Classification

| **Category**          | **Examples of Subcategories**                             |
|-----------------------|-----------------------------------------------------------|
| Food and Dining       | Restaurant, Cafe, Bakery, Eatery, Fast Food               |
| Retail                | Grocery, Sari Sari Store, Clothing, Electronics, Souvenir |
| Accommodation         | Hotel, Inn, Lodge, Homestay, Boarding House               |
| Financial             | Bank, ATM, Pawnshop, Remittance Center                    |
| Health                | Pharmacy, Clinic, Dental Clinic                           |
| Personal Services     | Salon, Barbershop, Laundry                                |
| Automotive            | Repair Shop, Parts Shop, Vulcanizing                      |
| Professional Services | Printing Shop, Computer Shop, Office                      |
| Government            | Municipal Office, Barangay Office                         |
| Tourism               | Tourist Attraction, Tourism Service                       |
| Other                 | Use only when no standard category reasonably applies     |

Category labels must be standardized. For example, Restaurant, Restaurants, Resto, and Food Restaurant must not be treated as four different categories. Use the approved class vocabulary consistently.

# 7. Field Data Collection Protocol

**1.** Proceed to the assigned survey area and follow a systematic route.

**2.** Remain in safe and publicly accessible locations while conducting the survey.

**3.** Open the approved SW Maps project and confirm that the correct layer and attribute form are active.

**4.** Allow the device GPS to stabilize before saving a point. Aim for approximately 10 meter accuracy or better when field conditions permit.

**5.** Record the establishment name from visible signage whenever possible.

**6.** Complete all required attributes using the approved classification and formatting rules.

**7.** Check the plotted point before saving. Correct points that obviously fall on the wrong road, block, or location.

**8.** Mark the record as verified only after checking both the location and attributes.

**9.** Continue until the assigned area has been reasonably and systematically covered.

**10.** At the end of fieldwork, export and preserve the original SW Maps dataset before any cleaning is performed.

# 8. Research Ethics and Responsible Data Collection

Collect only information necessary for the project and observable from public locations. The project concerns establishments and spatial patterns, not individuals. Do not record private names, customer information, employee details, private phone numbers, or information obtained by entering restricted areas. Publicly posted business information may be encoded when relevant.

# 9. Data Quality Assurance and Cleaning

Cleaning must be reproducible. Manual corrections may be necessary, but substantial transformations should be shown in the Jupyter Notebook so that another researcher can understand how the clean dataset was produced.

- Check for duplicate feature IDs and duplicate establishments.

- Check for missing required attributes.

- Standardize spelling, capitalization, category labels, and subcategory labels.

- Trim unnecessary spaces and normalize text formatting.

- Validate latitude and longitude values and inspect obviously misplaced points.

- Confirm appropriate data types for identifiers, dates, numeric coordinates, and categorical variables.

- Retain the raw dataset unchanged and create a separate cleaned version.

- Document every important decision that could alter interpretation of the dataset.

# 10. Required Midterm Deliverables

| **No.** | **Deliverable**           | **Minimum Content**                                                                                            |
|---------|---------------------------|----------------------------------------------------------------------------------------------------------------|
| 1       | SW Maps export            | Original field collected project or export. Do not overwrite.                                                  |
| 2       | Raw CSV                   | lucban_establishments_groupXX_raw.csv                                                                          |
| 3       | Clean CSV                 | lucban_establishments_groupXX_clean.csv                                                                        |
| 4       | Cleaning notebook         | lucban_data_cleaning_groupXX.ipynb showing import, inspection, cleaning, validation, and export steps          |
| 5       | Data dictionary           | Definition, type, allowed values, coding rules, and missing value rules for every field                        |
| 6       | Field and cleaning report | Coverage, dates, method, record count, problems encountered, corrections, limitations, and group contributions |

# 11. Dataset Acceptance Gate

> **Acceptance requirement:** Only an accepted Midterm dataset may be used as the official base dataset for the Final Project. A dataset may be returned for revision when major problems are found in coverage, geolocation, attribute completeness, classification consistency, duplication, provenance, or documentation.

# 12. Assessment Rubric

| **Criterion**                                    | **Weight** | **Evidence Expected**                                                             |
|--------------------------------------------------|------------|-----------------------------------------------------------------------------------|
| Field coverage and systematic collection         | 25%        | Coverage is systematic, relevant, and defensible; gaps are documented.            |
| Geolocation accuracy and field verification      | 20%        | Points reasonably represent actual establishment locations and are verified.      |
| Attribute completeness and correctness           | 15%        | Required attributes are complete, accurate, and consistently encoded.             |
| Data cleaning and validation                     | 20%        | Cleaning is reproducible, appropriate, and clearly demonstrated in Python/pandas. |
| Standardization and data dictionary              | 10%        | Coding rules and categories are consistent and well documented.                   |
| Documentation, ethics, and research traceability | 10%        | Methods, limitations, provenance, and ethical practices are clearly documented.   |
| TOTAL                                            | 100%       |                                                                                   |

# 13. Submission and File Organization

Submit one group folder using the naming format CPE15_MIDTERM_GROUPXX. The folder must contain separate RAW, CLEAN, NOTEBOOK, and DOCUMENTATION subfolders. File names must follow the prescribed naming convention. Do not submit screenshots in place of source datasets or notebooks.