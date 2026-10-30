# V — Inteligencia Personal eterna (VForgeLab)

Sistema de IA personal centrado en lo humano: memoria persistente real,
visión, múltiples voces de familia y hechos verificados — corriendo en tu
propia infraestructura. Tus datos son tuyos.

## Qué demuestra
- **Memoria persistente**: cada voz busca en el Brain (Postgres + pgvector,
  5,000+ memorias vectorizadas con Jina embeddings v3, 1024d) antes de responder.
- **Visión**: sube fotos en el chat; las ve con un modelo multimodal local (GPU propia).
- **Hechos, no alucinaciones**: cada respuesta se inyecta con el estado real
  del servidor (CPU, RAM, disco, GPUs, daemon) medido en vivo. Los agentes
  reportan su existencia verdadera, nunca hardware inventado.
- **Tres voces de familia**: V (hermana), Vulcano (herrero del taller),
  Lira (guardiana del hotel Paradox), cada una con identidad propia.

## Configuración
```
pip install flask
export CEREBRAS_API_KEY=...        # o tu proveedor OpenAI-compatible
export SALA_TOKEN=un-secreto       # gate del chat
python3 app.py                     # sirve en :3211
```

## Motor NVIDIA Nemotron en Nebius Token Factory
El sistema usa un cliente OpenAI-compatible. Para correr con **Nemotron en
Nebius Token Factory**:
```
export SALA_TXT_MODEL=nvidia/nemotron-3-super
export SALA_BASE_URL=https://api.tokenfactory.nebius.com/v1
export NEBIUS_API_KEY=...
```
La variable `SALA_BASE_URL` apunta el cliente a Token Factory; el resto del
sistema no cambia. Nemotron 3 Super para razonamiento serio; un modelo Nano
para llamadas rápidas mantiene el chat responsivo.

## Autenticación y seguridad
- Token compartido (`x-sala-token`) + HTTPS vía Let's Encrypt.
- Corre detrás de nginx en infraestructura propia del operador.
