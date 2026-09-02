# Proyecto DevOps — Comercial NovaTech S.A.C.

**Curso:** Herramientas de Desarrollo Profesional TIC  

---

## Integrantes del Grupo
* Capcha Hinostroza, Alvaro Alexis
* Cano Montes, Antoni
* Vilca Taipe, Jorge Florencio

---

## Objetivo del Proyecto
Probar la automatización del ciclo de vida del software para NovaTech S.A.C., reduciendo tiempos de despliegue de 90 a <5 minutos y errores en producción del 20% a <2% mediante contenedores y un pipeline CI/CD.

---

## Tecnologías Utilizadas
* **Lenguaje/Framework:** Python 3.14 / Flask
* **Control de versiones:** Git & GitHub
* **CI/CD:** GitHub Actions
* **Contenedorización:** Docker & Docker Hub
* **Infraestructura:** AWS EC2 & Terraform (IaC)
* **Calidad y Seguridad:** `flake8`, `unittest` y GitHub Encrypted Secrets

---

## Requisitos Previos
* Git v2.30+
* Python v3.10+
* Docker Engine / Desktop v20.10+
* Terminal (Bash, PowerShell o WSL2)

---

## Instrucciones de Ejecución Local y Contenedores
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/HerramientasDesarrolloProfesional-TIC-TA1.git
   cd HerramientasDesarrolloProfesional-TIC-TA1
   ```
2. Ejecución directa con Python:
   ```bash
   pip install -r requirements.txt
   python app.py
   # Acceso: http://localhost:4200
   ```
3. Construir y ejecutar con Docker:
   ```bash
   docker build -t novatech-web:1.0 .
   docker run --name novatech-app -d -p 4200:4200 novatech-web:1.0
   # Acceso: http://localhost:4200
   ```

---

## Explicación del Pipeline CI/CD
El flujo automatizado (`.github/workflows/ci-cd.yml`) ejecuta:
1. **Linting:** Valida sintaxis con `flake8`.
2. **Pruebas Unitarias (Quality Gate):** Ejecuta `unittest test.py`. Si falla, detiene todo el proceso.
3. **Build & Push:** Construye la imagen y la sube a Docker Hub.
4. **Deploy a AWS:** Conecta por SSH a AWS EC2, descarga la imagen y reemplaza el contenedor activo.

---

## Guía para Reproducir las Pruebas

### 1. Pruebas Exitosas (Local)
```bash
python3 test.py
# Resultado esperado: OK
```

### 2. Simulación de Fallo (Quality Gate)
1. Modificar `test.py` forzando un error (ej. esperar estado `500` en vez de `200`).
2. Verificar fallo local:
   ```bash
   python3 test.py
   # Resultado esperado: FAILED (failures=1)
   ```
3. Subir cambios a GitHub (`git push origin main`).
4. En la pestaña **Actions** de GitHub, la etapa de *Unit Tests* fallará en rojo (❌) y el despliegue a AWS se cancelará automáticamente.
