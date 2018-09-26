# -*- coding: utf-8 -*-
#!/usr/bin/env python
from app import app
import models

models.db.migrate(**app.config['DB_PARAMS'])
