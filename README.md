# Proyecto4---Recommendation


https://gist.github.com/jeremystan/c3b39d947d9b88b3ccff3147dbcf6c6b

# Explicación de Métricas en Reglas de Asociación

## 1. **Antecedents (Antecedentes)**

Se refiere al conjunto de productos o ítems en el **lado izquierdo** de la regla de asociación.

En una regla de asociación, el antecedente es el conjunto de productos que están relacionados con otro conjunto de productos en el consecuente.

**Ejemplo:**  
En la regla `{leche} → {pan}`, **antecedents** sería `{leche}`.

---

## 2. **Consequents (Consecuentes)**

Es el conjunto de productos en el **lado derecho** de la regla de asociación.

**Ejemplo:**  
En la regla `{leche} → {pan}`, **consequents** sería `{pan}`.

En otras palabras, los consecuentes son los productos que se compran con los productos del antecedente.

---

## 3. **Support (Soporte)**

El **soporte** de una regla mide qué tan frecuente ocurre la combinación de productos en el conjunto de datos.

Se define como la fracción de transacciones en las que aparece el conjunto de ítems (tanto el antecedente como el consecuente).

**Fórmula de Soporte:**

\[
Support(A → B) = \frac{Frecuencia(A \cap B)}{Número \, total \, de \, transacciones}
\]

**Ejemplo:**  
Si 1000 transacciones tienen el antecedente `{leche}` y 800 de ellas también contienen el consecuente `{pan}`, entonces el soporte de la regla `{leche} → {pan}` es:

\[
Support(leche → pan) = \frac{800}{1000} = 0.8 \, (80\%)
\]

---

## 4. **Confidence (Confianza)**

La **confianza** mide la probabilidad de que el consecuente ocurra dado que el antecedente ya ocurrió.

Es la probabilidad condicional de que el producto del consecuente esté en la cesta dado que el producto del antecedente ya está.

**Fórmula de Confianza:**

\[
Confidence(A → B) = \frac{Support(A \cup B)}{Support(A)}
\]

**Ejemplo:**  
Si 800 de las 1000 transacciones que contienen `{leche}` también contienen `{pan}`, entonces la confianza de la regla `{leche} → {pan}` es:

\[
Confidence(leche → pan) = \frac{800}{1000} = 0.8 \, (80\%)
\]

---

## 5. **Lift (Elevación)**

El **lift** mide qué tan relevante es una regla en comparación con la probabilidad de que los productos del consecuente ocurran por separado.

En otras palabras, el lift nos dice si los productos del antecedente y el consecuente ocurren juntos más frecuentemente de lo que esperaríamos por azar.

**Fórmula de Lift:**

\[
Lift(A → B) = \frac{Confidence(A → B)}{Support(B)}
\]

**Ejemplo:**  
Si la confianza de la regla `{leche} → {pan}` es 0.8 y el soporte de `{pan}` es 0.5 (50% de las transacciones contienen pan), entonces el lift sería:

\[
Lift(leche → pan) = \frac{0.8}{0.5} = 1.6
\]

Un **lift de 1** significa que los productos A y B ocurren juntos como se espera. Un **lift mayor que 1** indica que los productos ocurren juntos **más de lo esperado**, y un **lift menor que 1** indica que los productos ocurren **menos de lo esperado**.

---
