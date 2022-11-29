/**
 * User Settings JavaScript
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 1/2/2021
 * Updated: 11/29/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 */
import {
  changeEmail,
  getCurrentUser,
  updateUserDisplayName,
  updateUserPhoto,
} from '../firebase.js';
import {
  authRequest,
  deserializeForm,
  serializeForm,
  showNotification,
} from '../utils.js';

export const userSettings = {

  chooseUserPhoto() {
    /**
     * Choose a file to upload, triggers `uploadUserPhoto`.
     */
    const fileSelect = document.getElementById('userPhotoUrl');
    fileSelect.click();
  },

  initializeAccountForm() {
    /**
     * Initialize the user account form.
     */
    const fileElem = document.getElementById('userPhotoUrl');
    fileElem.addEventListener('change', uploadUserPhoto, false);
    this.resetAccountForm();
  },

  async resetAccountForm() {
    /**
     * Reset a form with currently saved data, replacing any changes.
     */
    const data = await authRequest('/api/users');
    const userForm = document.forms['user-form'];
    userForm.reset();
    deserializeForm(userForm, data);
  },

  async saveAccount() {
    /** 
    * Saves a user's account fields.
    */
    const user = getCurrentUser();
    const data = serializeForm('user-form');
    if (data.email !== user.email) {
      await changeEmail(data.email);
    }
    if (data.name !== user.displayName) {
      await updateUserDisplayName(data.name);
    }
    await authRequest('/api/users', data);
    const message = 'Your account data has been successfully saved.'
    showNotification('Account saved', message, /* type = */ 'success');
  },

  /**
   * Upload a user's photo through the API.
   */
   uploadUserPhoto,

};

export async function uploadUserPhoto() {
  /**
   * Upload a user's photo through the API.
   */
  if (this.files.length) {
    showNotification('Uploading photo', 'Uploading your profile picture...', /* type = */ 'wait');
    const downloadURL = await updateUserPhoto(this.files[0]);
    await authRequest('/api/users', { photo_url: downloadURL });
    const renderedUserPhotos = document.getElementsByClassName('user-photo-url');
    for (let i = 0, len = renderedUserPhotos.length; i < len; i++) {
      renderedUserPhotos[i].src = downloadURL;
    }
    showNotification('Uploading photo complete', 'Successfully uploaded your profile picture.', /* type = */ 'success');
  }
};
