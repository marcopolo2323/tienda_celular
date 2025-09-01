# Configuración de Gunicorn para producción

# Número de workers (2-4 x núcleos + 1)
workers = 3

# Tipo de worker
worker_class = 'gevent'

# Tiempo máximo de respuesta
timeout = 60

# Número máximo de conexiones simultáneas
max_requests = 1000
max_requests_jitter = 50

# Configuración de logs
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Configuración de seguridad
proc_name = 'tienda_celulares'

# Configuración de rendimiento
keepalive = 2