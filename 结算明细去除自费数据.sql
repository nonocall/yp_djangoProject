ALTER TABLE "医保门诊结算明细" RENAME TO "医保门诊结算明细全量";
ALTER TABLE "医保住院结算明细" RENAME TO "医保住院结算明细全量";


create table "医保门诊结算明细" as
SELECT * FROM "医保门诊结算明细全量"  where "自付比例" != '1';


create table "医保住院结算明细" as
SELECT * FROM "医保住院结算明细全量"  where "自付比例" != '1';


-- 住院明细
CREATE INDEX idx_zymx_settlement_document_number2 ON "医保住院结算明细" ("结算单据号");
CREATE INDEX idx_zymx_project_usage_date2 ON "医保住院结算明细" ("项目使用日期");
CREATE INDEX idx_zymx_settlement_date2 ON "医保住院结算明细" ("结算日期");
CREATE INDEX idx_zymx_hospital_project_code2 ON "医保住院结算明细" ("医院项目编码");
CREATE INDEX idx_zymx_medical_project_code2 ON "医保住院结算明细" ("医保项目编码");
CREATE INDEX idx_zymx_project_order_date2 ON "医保住院结算明细" ("项目开单日期");
CREATE INDEX idx_zymx_hospital_project_name2 ON "医保住院结算明细" ("医院项目名称");
CREATE INDEX idx_zymx_medical_project_name2 ON "医保住院结算明细" ("医保项目名称");


-- 门诊明细
CREATE INDEX idx_mzmx_settlement_document_number2 ON "医保门诊结算明细" ("结算单据号");
CREATE INDEX idx_mzmx_project_usage_date2 ON "医保门诊结算明细" ("项目使用日期");
CREATE INDEX idx_mzmx_settlement_date2 ON "医保门诊结算明细" ("结算日期");
CREATE INDEX idx_mzmx_hospital_project_code2 ON "医保门诊结算明细" ("医院项目编码");
CREATE INDEX idx_mzmx_medical_project_code2 ON "医保门诊结算明细" ("医保项目编码");
CREATE INDEX idx_mzmx_project_order_date2 ON "医保门诊结算明细" ("项目开单日期");
CREATE INDEX idx_mzmx_hospital_project_name2 ON "医保门诊结算明细" ("医院项目名称");
CREATE INDEX idx_mzmx_medical_project_name2 ON "医保门诊结算明细" ("医保项目名称");










