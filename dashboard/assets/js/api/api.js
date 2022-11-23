/**
 * API Interface
 * Copyright (c) 2022 Cannabis Data
 * Copyright (c) 2021-2022 Cannlytics
 * 
 * Authors:
 *    Keegan Skeate <https://github.com/keeganskeate>
 * Created: 4/24/2021
 * Updated: 11/22/2022
 * License: MIT License <https://github.com/cannabisdata/cannabisdata/blob/main/LICENSE>
 * 
 * Description: The `api` object interfaces with the Cannlytics API to send
 * and retrieve data to and from the back-end, where data is processed and
 * stored in the Firestore database and Metrc API.
 */
import { authRequest } from '../utils.js';
 
export const api = {

  /*----------------------------------------------------------------------------
   * Organizations
   *--------------------------------------------------------------------------*/
 
  getOrganization: (id) => authRequest(`/api/organizations/${id}`),
  getOrganizations: (params) => authRequest('/api/organizations', null, { params }),
  createOrganizations: (data) => authRequest('/api/organizations', data),
  updateOrganizations: (data) => authRequest('/api/organizations', data),
  deleteOrganizations: (data) => authRequest('/api/organizations', data, { delete: true }),
  getOrganizationSettings: (orgId) => authRequest(`/api/organizations/${orgId}/settings`),
  updateOrganizationSettings: (orgId, data) => authRequest(`/api/organizations/${orgId}/settings`, data),

  /*----------------------------------------------------------------------------
   * Users
   *--------------------------------------------------------------------------*/
 
  getUser: (id) => authRequest(`/api/users/${id}`),
  getUsers: (params) => authRequest('/api/users', null, { params }),
  createUser: (data) => authRequest('/api/users', data),
  updateUser: (data) => authRequest('/api/users', data),
  deleteUser: (data) => authRequest('/api/users', data, { delete: true }),
  getUserSettings: (userId) => authRequest(`/api/users/${userId}/settings`),
  updateUserSettings: (userId, data) => authRequest(`/api/users/${userId}/settings`, data),

}
