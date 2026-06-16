-- migrate_product_categories.sql
-- Re-clasifica products.category para productos importados desde fuentes externas
-- (inciapi.com / Open Beauty Facts) que usan una taxonomía distinta.
--
-- Aplica el mismo keyword matching que _infer_category() en db_writer.py.
-- Solo actualiza productos cuya categoría NO sea ya parte de la taxonomía estándar.
-- Los productos ya correctamente categorizados por el scraper de INCIDecoder
-- (cleanser, moisturizer, spf, serum, exfoliant, retinoid, toner, eye, mask, oil, spot, other)
-- NO son tocados.
--
-- Correr desde psql o DBeaver contra la BD de desarrollo:
--   \i scripts/migrate_product_categories.sql
-- O desde CLI:
--   psql $DATABASE_URL -f scripts/migrate_product_categories.sql

BEGIN;

-- ── Paso 1: marcar como 'other' todo lo que no es taxonomía estándar ──────────
-- Esto incluye categorías de Open Beauty Facts (hygiene, non-food-products,
-- cosmetic-products, Cosmetics, Skincare, Beauty, Haircare, etc.)
-- y cualquier NULL o categoría desconocida.

UPDATE products
SET category = 'other'
WHERE category IS NULL
   OR category NOT IN (
       'cleanser', 'moisturizer', 'spf', 'serum',
       'exfoliant', 'retinoid', 'toner', 'eye',
       'mask', 'oil', 'spot', 'other'
   );

-- ── Paso 2: clasificar por keywords (misma lógica que db_writer._infer_category) ──
-- El orden importa: la primera regla que matchea gana.
-- Más específico primero (retinoid, spf, spot) → menos específico al final (moisturizer).

-- retinoid (antes de exfoliant porque adapalene/tretinoin pueden confundirse)
UPDATE products
SET category = 'retinoid'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%retinol%'   OR
      lower(name) LIKE '%retinoid%'  OR
      lower(name) LIKE '%adapalene%' OR
      lower(name) LIKE '%differin%'  OR
      lower(name) LIKE '%tretinoin%'
  );

-- spot treatment
UPDATE products
SET category = 'spot'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%spot%'          OR
      lower(name) LIKE '%blemish%'       OR
      lower(name) LIKE '%drying lotion%' OR
      lower(name) LIKE '%acne patch%'
  );

-- spf / sunscreen
UPDATE products
SET category = 'spf'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%spf%'          OR
      lower(name) LIKE '%sunscreen%'    OR
      lower(name) LIKE '%sunblock%'     OR
      lower(name) LIKE '%solar%'        OR
      lower(name) LIKE '%anthelios%'    OR
      lower(name) LIKE '%ultra sheer%'  OR
      lower(name) LIKE '%sun cream%'    OR
      lower(name) LIKE '%protector%'    OR
      lower(name) LIKE '%soleil%'
  );

-- cleanser
UPDATE products
SET category = 'cleanser'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%cleanser%'       OR
      lower(name) LIKE '%cleansing%'      OR
      lower(name) LIKE '%face wash%'      OR
      lower(name) LIKE '%gel lavant%'     OR
      lower(name) LIKE '%gel limpiador%'  OR
      lower(name) LIKE '%mousse%'         OR
      lower(name) LIKE '%micellar%'       OR
      lower(name) LIKE '%micelaire%'      OR
      lower(name) LIKE '%démaquillant%'   OR
      lower(name) LIKE '%agua micelar%'
  );

-- serum
UPDATE products
SET category = 'serum'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%serum%' OR
      lower(name) LIKE '%sérum%' OR
      lower(name) LIKE '%séro%'
  );

-- exfoliant
UPDATE products
SET category = 'exfoliant'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%exfoliant%' OR
      lower(name) LIKE '%exfoliat%'  OR
      lower(name) LIKE '% aha %'     OR
      lower(name) LIKE '% bha %'     OR
      lower(name) LIKE '%peel%'      OR
      lower(name) LIKE '%peeling%'
  );

-- toner
UPDATE products
SET category = 'toner'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%toner%'   OR
      lower(name) LIKE '%essence%' OR
      lower(name) LIKE '%lotion p%'   -- "lotion P" en marcas francesas = toner
  );

-- eye cream
UPDATE products
SET category = 'eye'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%eye cream%'   OR
      lower(name) LIKE '%eye gel%'     OR
      lower(name) LIKE '%contorno%'    OR
      lower(name) LIKE '%contour%'     OR
      lower(name) LIKE '%yeux%'        OR
      lower(name) LIKE '%occhi%'
  );

-- mask
UPDATE products
SET category = 'mask'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%mask%'       OR
      lower(name) LIKE '%mascarilla%' OR
      lower(name) LIKE '%masque%'
  );

-- oil (facial, no body/hair)
UPDATE products
SET category = 'oil'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%facial oil%' OR
      lower(name) LIKE '%face oil%'   OR
      lower(name) LIKE '%huile%'
  );

-- moisturizer — al final, más amplio
UPDATE products
SET category = 'moisturizer'
WHERE category = 'other'
  AND (
      lower(name) LIKE '%moisturizer%'   OR
      lower(name) LIKE '%moisturising%'  OR
      lower(name) LIKE '%moisturizing%'  OR
      lower(name) LIKE '%hydrat%'        OR
      lower(name) LIKE '%hydrant%'       OR
      lower(name) LIKE '%face cream%'    OR
      lower(name) LIKE '%facial cream%'  OR
      lower(name) LIKE '%crème%'         OR
      lower(name) LIKE '%creme%'         OR
      lower(name) LIKE '%crema%'         OR
      lower(name) LIKE '%barrier cream%'
  );

-- ── Resultado ──────────────────────────────────────────────────────────────────
SELECT
    category,
    COUNT(*) AS productos
FROM products
GROUP BY category
ORDER BY productos DESC;

COMMIT;
