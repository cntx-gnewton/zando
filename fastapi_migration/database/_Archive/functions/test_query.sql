WITH genetic_results AS (
    SELECT * FROM generate_genetic_analysis_section(CAST('{"rs16891982","rs4880","rs1800795","rs743572"}' AS text[]))
) 
SELECT generate_summary_section(
    CAST('{"rs16891982","rs4880","rs1800795","rs743572"}' AS text[]),
    (SELECT * FROM genetic_results)
);