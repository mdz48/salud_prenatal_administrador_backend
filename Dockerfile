FROM python:3.11-slim

WORKDIR /app

# Copiar requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el codigo fuente
COPY . .

# Exponer puerto 8002
EXPOSE 8002

# Comando para iniciar el servicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
