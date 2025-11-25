# Data Quality (DQ) Rules – For AI Data Profiler (PADS/ATF Simulation)

This document defines all Data Quality rules used by the AI Data Profiler, aligned with the ATF Profiler logic from the PADS project.

---

## 1. Mandatory DQ Rules (Applied to All Columns)

### **Null Check**
- Fail if Null% exceeds 5%.
- Ensures column completeness before profiling.

### **Distinct Count Check**
- Detect sparse columns: Distinct% < 0.5%.
- Detect high-cardinality columns: Distinct% > 95%.
- Helps determine suitability for profiling.

### **Duplicate RecordId Check**
- RecordId must be unique.
- Fail if duplicates exist.

### **Data Type Validation**
- Each value must match the column’s expected datatype.

### **Allowed Value Check**
Valid values:
- **Movement:** `CALO, FCOP, SALE, FUTR, ADJM, MISC`
- **CurrencyCode:** `USD, INR, GBP, EUR`
- **BuySell:** `BUY, SELL`
- **InstrumentType:** `E, F, D, B`

---

## 2. Column-Level Rules

### **POLICY_ID**
- Must not be NULL.
- Must be unique.

### **PremiumAmount**
- Range must be: `1000 – 20000`
- Detect outliers.
- Compute quartiles (Q1–Q4).

### **Description**
- Optional, but if majority null → grade as low-quality.

---

## 3. Cross-Column Relationship Rules

### **Movement ↔ Description Consistency**
- CALO → Description contains “CASH”
- FCOP → Description contains “COMMISSION”
- FUTR → Description contains “FUTURE”
- SALE → Description contains “SALE”

### **CurrencyCode ↔ Region Consistency**
- USD → NA
- GBP → EMEA
- INR → APAC
- EUR → EMEA or LATAM (adjustable)

### **PremiumAmount ↔ Movement**
Profiler checks abnormal amounts for certain movement types.

---

## 4. Distribution-Based Rules (Used for Profiling)

### **Value Distribution Rule**

### **VarianceType: ALL**
Applied to categorical columns:
- Movement  
- CurrencyCode  
- InstrumentType  
- PolicyType  
- Region

Selects a representative RecordId for:
- Top bucket
- Middle bucket
- Low-frequency bucket

### **VarianceType: Range**
Numeric column range grouping:
- 1000–5000  
- 5000–10000  
- 10000–15000  
- 15000–20000

### **VarianceType: TopValue**
Pick trades representing:
- Top Movement
- Top Currency
- Top Region

### **VarianceType: PositiveNegative**
Used if numeric values include negatives.

---

## 5. New Column Filter Rule (Incremental Profiling Logic)

When a new column is added:
1. Set `{TLA}_Filter = 'NEW_COLUMN'`
2. Profiler runs **only on the new column**
3. Results are merged with existing profiling outputs

This avoids full-table re-profiling.

---

# End of Document
