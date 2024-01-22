SELECT 
    b.block_number,
    SUM(t.value) 
AS 
    total_value 
FROM 
    blocks b 
JOIN 
    transactions t
ON
    b.block_number = t.block_number 
WHERE
    b.timestamp >= '2024-01-01 00:00:00' AND b.timestamp <= '2024-01-01 00:30:00' 
GROUP BY
    b.block_number 
ORDER BY
    total_value 
DESC
LIMIT 1;
