/**
 * Main JavaScript Module
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 11/22/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 */
import { analytics } from './analytics/analytics.js';
import { api } from './api/api.js';
import { app } from './app/app.js';
import { auth } from './auth/auth.js';
import { dashboard } from './dashboard/dashboard.js';
import * as firebase from './firebase.js';
import { payments } from './settings/payments.js';
import { settings } from './settings/settings.js';
import { theme } from './settings/theme.js';
import { ui } from './ui/ui.js';
import { utils } from './utils.js';

// Stylesheets
import '../css/main.scss';
import '../css/layout.scss';
import '../css/colors.scss';
import '../css/code.scss';

// Modules
export {
  analytics,
  api,
  app,
  auth,
  dashboard,
  firebase,
  payments,
  settings,
  theme,
  ui,
  utils,
}
