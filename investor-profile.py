import streamlit as st
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

from experta import KnowledgeEngine, Fact, Rule, Field, MATCH, TEST, AS

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

class TipoInversor(Fact):
     tipo = Field(str, mandatory=True)

# --- Recomendación final ---
class Recomendacion(Fact):
    detalle = Field(str, mandatory=True)
    instrumentos = Field(dict, mandatory=True)

# ==========================
# 2. Motor de Inferencia
# ==========================
class MotorInversor(KnowledgeEngine):

   # --- CONSERVADOR ---
    @Rule(
        Perfil(tolerancia='baja', experiencia=MATCH.e, reaccion_perdidas=MATCH.r, horizonte=MATCH.h, objetivo=MATCH.o, porcentaje_inversion=MATCH.p, edad=MATCH.edad),
        TEST(lambda e, r, h, o, p, edad:
             e in ('ninguna', 'moderada', 'amplia') and
             r in ('vende', 'mantiene') and
             h in ('corto', 'mediano') and
             o == 'preservar' and
             p in ('bajo', 'medio') and
             edad in ('joven','adulto', 'mayor'))
    )
    def conservador(self):
        self.declare(TipoInversor(tipo='conservador'))


    # --- MODERADO ---
    @Rule(
        Perfil(tolerancia='media', experiencia=MATCH.e, reaccion_perdidas=MATCH.r, horizonte=MATCH.h, objetivo=MATCH.o, porcentaje_inversion=MATCH.p, edad=MATCH.edad),
        TEST(lambda e, r, h, o, p, edad:
             e in ('moderada', 'amplia') and
             r in ('mantiene', 'compra') and
             h in ('mediano', 'largo') and
             o == 'equilibrado' and
             p in ('medio', 'alto') and
             edad in ('joven', 'adulto'))
    )
    def moderado(self):
        self.declare(TipoInversor(tipo='moderado'))


    # --- ARRIESGADO ---
    @Rule(
        Perfil(tolerancia='alta', experiencia=MATCH.e, reaccion_perdidas=MATCH.r, horizonte=MATCH.h, objetivo=MATCH.o, porcentaje_inversion=MATCH.p, edad=MATCH.edad),
        TEST(lambda e, r, h, o, p, edad:
             e in ('moderada', 'amplia') and
             r in ('mantiene', 'compra') and
             h in ('corto', 'mediano', 'largo')  and
             o in ('equilibrado','maximizar')  and
             p in ('bajo','medio', 'alto') and
             edad in ('joven', 'adulto'))
    )
    def arriesgado(self):
        self.declare(TipoInversor(tipo='arriesgado'))


    # --- CASOS INTERMEDIOS ---
    @Rule(
        Perfil(tolerancia='baja', reaccion_perdidas='compra')
    )
    def moderado_por_reaccion(self):
        self.declare(TipoInversor(tipo='moderado'))

    @Rule(
        Perfil(tolerancia='media', experiencia='ninguna', reaccion_perdidas='vende')
    )
    def conservador_por_falta_experiencia(self):
        self.declare(TipoInversor(tipo='conservador'))

    @Rule(
        Perfil(tolerancia='alta', experiencia='moderada', reaccion_perdidas='mantiene')
    )
    def moderado_por_cautela(self):
        self.declare(TipoInversor(tipo='moderado'))

    @Rule(
        AS.p << Perfil(),
        salience=-10  # prioridad baja, se ejecuta solo si nada más aplicó
    )
    def default_tipo(self, p):
      self.declare(TipoInversor(tipo='moderado'))


    # === 2. Recomendaciones según tipo y otros atributos ===
    @Rule(TipoInversor(tipo='conservador'),
          Perfil(horizonte=MATCH.h, objetivo=MATCH.o),
          TEST(lambda h, o: h in ['corto', 'mediano'] and o == 'preservar'))
    def recomendacion_conservador(self, h, o):
        self.declare(Recomendacion(
            detalle="Invertir en instrumentos líquidos y seguros.",
            instrumentos={
                "FCI rescate inmediato": 40,
                "FCI Money Market": 30,
                "Letras del Tesoro": 20,
                "Caución": 10
            }
        ))

    @Rule(TipoInversor(tipo='moderado'),
          Perfil(horizonte=MATCH.h, objetivo=MATCH.o),
          TEST(lambda h, o: h in ['mediano', 'largo'] and o in ['equilibrado', 'maximizar']))
    def recomendacion_moderado(self):
        self.declare(Recomendacion(
            detalle="Diversificar entre renta fija y variable.",
            instrumentos={
                "FCI de renta fija": 25,
                "ON de empresas reconocidas": 25,
                "Bonos del Estado": 20,
                "Acciones argentinas": 15,
                "FCI de acciones": 15
            }
        ))

    @Rule(TipoInversor(tipo='arriesgado'),
          Perfil(horizonte='largo', objetivo='maximizar'))
    def recomendacion_arriesgado(self):
        self.declare(Recomendacion(
            detalle="Incluir activos de renta variable y exposición internacional.",
            instrumentos={
                "Acciones argentinas": 30,
                "FCI de acciones": 25,
                "Cedears tecnológicas": 20,
                "Cedears de consumo masivo": 15,
                "Bonos del Estado": 10
            }
        ))

     # === 3️⃣ Recomendaciones por defecto (si no se cumple ninguna específica) ===
    @Rule(TipoInversor(tipo='conservador'),
          ~Recomendacion(detalle=MATCH.any))
    def recomendacion_conservador_base(self):
        self.declare(Recomendacion(
            detalle="Perfil conservador: priorizar estabilidad y baja volatilidad.",
            instrumentos={
                "FCI Money Market": 50,
                "Bonos del Estado": 30,
                "Caución": 20
            }
        ))

    @Rule(TipoInversor(tipo='moderado'),
          ~Recomendacion(detalle=MATCH.any))
    def recomendacion_moderado_base(self):
        self.declare(Recomendacion(
            detalle="Perfil moderado: equilibrio entre renta fija y variable.",
            instrumentos={
                "FCI de renta fija": 30,
                "Bonos del Estado": 25,
                "Acciones argentinas": 25,
                "FCI de acciones": 20
            }
        ))

    @Rule(TipoInversor(tipo='arriesgado'),
          ~Recomendacion(detalle=MATCH.any))
    def recomendacion_arriesgado_base(self):
        self.declare(Recomendacion(
            detalle="Perfil arriesgado: priorizar crecimiento y exposición a riesgo.",
            instrumentos={
                "Acciones argentinas": 35,
                "FCI de acciones": 25,
                "Cedears tecnológicas": 20,
                "Cedears de consumo masivo": 10,
                "Bonos del Estado": 10
            }
        ))

    @Rule(Recomendacion())
    def detener_inferencia(self):
        self.halt()
# ==========================
# 3. INTERFAZ STREAMLIT
# ==========================
def main():
    st.title("🧠 Sistema Experto: Tipo de Inversor")

    ## Inputs del usuario
    edad = st.selectbox("Edad", ["Seleccione una opción", "joven", "adulto", "mayor"])
    horizonte = st.selectbox("Horizonte de inversión", ["Seleccione una opción", "corto", "mediano", "largo"])
    tolerancia = st.selectbox("Tolerancia al riesgo", ["Seleccione una opción", "baja", "media", "alta"])
    experiencia = st.selectbox("Experiencia en inversiones", ["Seleccione una opción", "ninguna", "moderada", "amplia"])
    reaccion_perdidas = st.selectbox("Reacción ante pérdidas", ["Seleccione una opción", "vende", "mantiene", "compra"])
    objetivo = st.selectbox("Objetivo principal", ["Seleccione una opción", "preservar", "equilibrado", "maximizar"])
    porcentaje_inversion = st.selectbox("Porcentaje del ingreso que puede invertir", ["Seleccione una opción", "bajo", "medio", "alto"])

    # Texto por defecto
    st.markdown("---")
    resultado_placeholder = st.empty()
    resultado_placeholder.info("💬 Seleccione un tipo y presione 'Calcular tipo de inversor'")

    # --- Boton  ---
    calcular = st.button("Calcular tipo de inversor ✅")


    if calcular:
         # Validar que no haya "Seleccione una opción"
        campos = [edad, horizonte, tolerancia, experiencia, reaccion_perdidas, objetivo, porcentaje_inversion]
        if any(c == "Seleccione una opción" for c in campos):
            resultado_placeholder.warning("⚠️ Por favor, completá todas las opciones antes de continuar.")
        else:
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
          recomendacion = None

          for fact in engine.facts.values():
              if isinstance(fact, TipoInversor):
                  tipo_inversor = fact["tipo"]
              elif isinstance(fact, Recomendacion):
                  recomendacion = fact

                  # --- Mostrar resultados ---
                  if tipo_inversor:
                      st.success(f"✅ Tipo de inversor: **{tipo_inversor.upper()}**")

                      if recomendacion:
                          st.markdown(f"### 💡 Recomendación:")
                          st.info(recomendacion["detalle"])

                          st.markdown("#### 📊 Distribución sugerida:")
                          for instrumento, porcentaje in recomendacion["instrumentos"].items():
                              st.write(f"- **{instrumento}** → {porcentaje}%")
                      else:
                          st.warning("⚠️ No se encontró una recomendación específica para este perfil.")
                  else:
                      st.warning("⚠️ No se pudo determinar el tipo de inversor. Revisá las respuestas.")


if __name__ == "__main__":
    main()