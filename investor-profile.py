import streamlit as st
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

from experta import KnowledgeEngine, Fact, Rule, Field, MATCH, TEST

# ==========================
# 1. Definición de Hechos
# ==========================
class Perfil(Fact):
    edad = Field(str, mandatory=False)
    horizonte = Field(str, mandatory=False)
    tolerancia = Field(str, mandatory=False)
    experiencia = Field(str, mandatory=False)
    reaccion_perdidas = Field(str, mandatory=False)
    objetivo = Field(str, mandatory=False)
    porcentaje_inversion = Field(str, mandatory=False)

# ==========================
# 2. Motor de Inferencia
# ==========================
class MotorInversor(KnowledgeEngine):

    # ---- Reglas para Inversor Conservador ----
    @Rule(
        Perfil(tolerancia='baja', horizonte=MATCH.h, objetivo='preservar'),
        TEST(lambda h: h in ('corto', 'mediano'))
    )
    def perfil_conservador(self):
        self.declare(Fact(tipo_inversor='conservador'))

    @Rule(
        Perfil(edad='mayor', experiencia='ninguna', reaccion_perdidas='vende')
    )
    def perfil_conservador2(self):
        self.declare(Fact(tipo_inversor='conservador'))

    @Rule(
        Perfil(tolerancia='baja', porcentaje_inversion='bajo')
    )
    def perfil_conservador3(self):
        self.declare(Fact(tipo_inversor='conservador'))

    # ---- Reglas para Inversor Moderado ----
    @Rule(
        Perfil(tolerancia='media', horizonte='mediano', objetivo='equilibrado')
    )
    def perfil_moderado(self):
        self.declare(Fact(tipo_inversor='moderado'))

    @Rule(
        Perfil(edad='adulto', experiencia='moderada', reaccion_perdidas='mantiene')
    )
    def perfil_moderado2(self):
        self.declare(Fact(tipo_inversor='moderado'))

    @Rule(
        Perfil(tolerancia='media', porcentaje_inversion='medio')
    )
    def perfil_moderado3(self):
        self.declare(Fact(tipo_inversor='moderado'))

    # ---- Reglas para Inversor Arriesgado ----
    @Rule(
        Perfil(tolerancia='alta', horizonte='largo', objetivo='maximizar')
    )
    def perfil_arriesgado(self):
        self.declare(Fact(tipo_inversor='arriesgado'))

    @Rule(
        Perfil(edad='joven', experiencia='amplia', reaccion_perdidas='compra')
    )
    def perfil_arriesgado2(self):
        self.declare(Fact(tipo_inversor='arriesgado'))

    @Rule(
        Perfil(tolerancia='alta', porcentaje_inversion='alto')
    )
    def perfil_arriesgado3(self):
        self.declare(Fact(tipo_inversor='arriesgado'))

# ==========================
# 3. INTERFAZ STREAMLIT
# ==========================
def main():
    st.title("🧠 Sistema Experto: Tipo de Inversor")

    # Inputs del usuario
    edad = st.selectbox("Edad", ["joven", "adulto", "mayor"])
    horizonte = st.selectbox("Horizonte de inversión", ["corto", "mediano", "largo"])
    tolerancia = st.selectbox("Tolerancia al riesgo", ["baja", "media", "alta"])
    experiencia = st.selectbox("Experiencia en inversiones", ["ninguna", "moderada", "amplia"])
    reaccion_perdidas = st.selectbox("Reacción ante pérdidas", ["vende", "mantiene", "compra"])
    objetivo = st.selectbox("Objetivo principal", ["preservar", "equilibrado", "maximizar"])
    porcentaje_inversion = st.selectbox("Porcentaje del ingreso que puede invertir", ["bajo", "medio", "alto"])

    if st.button("Calcular tipo de inversor"):
        engine = MotorInversor()
        engine.reset()
        engine.declare(Perfil(
            edad=edad,
            horizonte=horizonte,
            tolerancia=tolerancia,
            experiencia=experiencia,
            reaccion_perdidas=reaccion_perdidas,
            objetivo=objetivo,
            porcentaje_inversion=porcentaje_inversion
        ))

        engine.run()

        # Extraer el tipo de inversor declarado
        tipo_inversor = None
        for fact in engine.facts.values():
            if isinstance(fact, Fact) and "tipo_inversor" in fact:
                tipo_inversor = fact["tipo_inversor"]
                break

        if tipo_inversor:
            st.success(f"✅ Tipo de inversor: {tipo_inversor.upper()}")
            if tipo_inversor == "conservador":
                st.info("➡️ Recomendación: instrumentos seguros (plazos fijos, bonos soberanos, fondos de renta fija).")
            elif tipo_inversor == "moderado":
                st.info("➡️ Recomendación: combinar renta fija y variable (ETF, bonos corporativos, fondos mixtos).")
            elif tipo_inversor == "arriesgado":
                st.info("➡️ Recomendación: incluir renta variable, criptomonedas o startups (mayor riesgo, mayor potencial).")
        else:
            st.warning("⚠️ No se pudo determinar el tipo de inversor. Revisá las respuestas.")

if __name__ == "__main__":
    main()
