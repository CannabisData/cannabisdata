/**
 * Analytics JavaScript
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2021 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 8/1/2021
 * Updated: 11/22/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 */

// Import any needed charting libraries.
// import Chart from 'chart.js';
// import "chartjs-chart-box-and-violin-plot/build/Chart.BoxPlot.js";

import { authRequest, deserializeForm, serializeForm, showNotification } from '../utils.js';

export const analytics = {

  initialize() {
    /**
     * Initialize analytics.
     */
  },

  getAnalytics() {
    /**
     * Get analytics through the API.
     */
    const form = document.getElementById('analytics-form');
    const data = serializeForm(form);
    authRequest('/api/analytics', data).then((response) => {
      if (response.error) {
        showNotification('Error getting analytics', response.message, { type: 'error' });
      } else {
        // TODO: Render the analytics in the user interface.
        document.getElementById('output').classList.remove('d-none');
        document.getElementById('output-message').textContent = JSON.stringify(response.data);
      }
    });
  },

}
