/**
 * Settings JavaScript
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2020-2021 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/3/2020
 * Updated: 11/22/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 */
import { apiSettings } from './api.js';
import { errorSettings } from './errors.js';
import { helpSettings } from './help.js';
import { organizationSettings } from './organizations.js';
import { userSettings } from './user.js';

export const settings = {
  ...apiSettings,
  ...errorSettings,
  ...helpSettings,
  ...organizationSettings,
  ...userSettings,
};
