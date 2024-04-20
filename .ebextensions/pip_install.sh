commands:
  01_upgrade_pip:
    command: '/opt/python/run/venv/bin/pip install --upgrade pip && /opt/python/run/venv/bin/pip install weasyprint'
    ignoreErrors: false