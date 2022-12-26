/**
 * App JavaScript
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 12/7/2020
 * Updated: 12/4/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 */
import { checkForCredentials } from '../auth/auth.js';
import { onAuthChange } from '../firebase.js';
import { authRequest } from '../utils.js';
import { initHelpers, navigationHelpers } from '../ui/ui.js';
import { dataTables } from './dataTables.js';
import { dataModels } from './dataModels.js';

export const app = {

  ...dataModels,
  ...dataTables,

  initialize(redirect=false) {
    /**
     * Initialize the app's features and functionality.
     * @param {Boolean} redirect Whether to redirect the user to the dashboard (optional).
     */

    // Enable any and all tooltips.
    initHelpers.initializeTooltips();

    // Hide the main content and show a splash page while the user is loading.
    try {
      document.getElementById('splash').classList.remove('d-none');
    } catch(error) {
      // Splash page is probably not included on this page.
    }

    // Create a session when a user is detected, checking for any Google credentials.
    onAuthChange(async (user) => {
      if (user) {
        if (user.metadata.createdAt == user.metadata.lastLoginAt) {
          const { email } = user;
          // TODO: Use your own custom domain for production.
          const defaultPhoto = `https://cannlytics.com/robohash/${user.uid}?width=60&height=60`;
          const data = { email, photo_url: defaultPhoto };
          await authRequest('/api/users', data);
        }
        // Only authenticate with the server as needed.
        const currentSession = this.getSessionCookie();
        if (currentSession === 'None') await authRequest('/src/auth/login');
        if (redirect) window.location.href = window.location.origin;
        document.getElementById('splash').classList.add('d-none');
        document.getElementById('page').classList.remove('d-none');
      } else {
        // If the user has not persisted their session, then log out of their
        // Django session, and redirect to the sign in page.
        await checkForCredentials();
        const currentSession = this.getSessionCookie();
        if (currentSession === 'None') await authRequest('/src/auth/logout');
        if (!window.location.href.includes('account')) {
          window.location.href = `${window.location.origin}\\account\\sign-in`;
          await page.waitForNavigation();
        }
        document.getElementById('page').classList.remove('d-none');
      }
    });

    // Hide the sidebar on small screens.
    try {
      navigationHelpers.toggleSidebar('sidebar-menu');
    } catch(error) { /* User not signed in. */}

  },

  getSessionCookie(nullValue='None') {
    /** Gets the session cookie, returning 'None' by default if the cookie is null. */
    return (document.cookie.match(/^(?:.*;)?\s*__session\s*=\s*([^;]+)(?:.*)?$/)||[,nullValue])[1];
  },

}
