import React, { useState } from 'react';
import { FaUser, FaLock, FaHistory, FaFileAlt, FaSignOutAlt, FaDna, FaUpload } from 'react-icons/fa';

const AccountPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'history'>('profile');
  
  // Mock user data
  const user = {
    name: 'Test User',
    email: 'test@example.com',
    created_at: new Date(2023, 5, 15).toLocaleDateString()
  };
  
  return (
    <div className="py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Account Settings</h1>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="flex border-b border-gray-200">
          <button
            className={`px-6 py-3 font-medium text-sm ${
              activeTab === 'profile'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('profile')}
          >
            <FaUser className="inline mr-2" />
            Profile
          </button>
          <button
            className={`px-6 py-3 font-medium text-sm ${
              activeTab === 'security'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('security')}
          >
            <FaLock className="inline mr-2" />
            Security
          </button>
          <button
            className={`px-6 py-3 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('history')}
          >
            <FaHistory className="inline mr-2" />
            Activity
          </button>
        </div>
        
        <div className="p-6">
          {activeTab === 'profile' && (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    id="name"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    defaultValue={user.name}
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    defaultValue={user.email}
                  />
                </div>
                <div>
                  <button
                    type="button"
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Save Changes
                  </button>
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Account Information</h2>
                <div className="bg-gray-50 rounded-md p-4">
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Member since</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user.created_at}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Account type</dt>
                      <dd className="mt-1 text-sm text-gray-900">Free</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Reports generated</dt>
                      <dd className="mt-1 text-sm text-gray-900">5</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">DNA files</dt>
                      <dd className="mt-1 text-sm text-gray-900">2</dd>
                    </div>
                  </dl>
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-lg font-medium text-red-600 mb-4">Danger Zone</h2>
                <p className="text-sm text-gray-500 mb-4">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <button
                  type="button"
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Delete Account
                </button>
              </div>
            </div>
          )}
          
          {activeTab === 'security' && (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Change Password</h2>
              <div className="space-y-4">
                <div>
                  <label htmlFor="current-password" className="block text-sm font-medium text-gray-700">
                    Current Password
                  </label>
                  <input
                    type="password"
                    name="current-password"
                    id="current-password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="new-password" className="block text-sm font-medium text-gray-700">
                    New Password
                  </label>
                  <input
                    type="password"
                    name="new-password"
                    id="new-password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    name="confirm-password"
                    id="confirm-password"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                <div>
                  <button
                    type="button"
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Update Password
                  </button>
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Login Sessions</h2>
                <div className="space-y-3">
                  <div className="bg-green-50 border border-green-100 rounded-md p-4 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Current Session</p>
                      <p className="text-sm text-gray-500">MacOS - Chrome - California, USA</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  </div>
                  <button
                    type="button"
                    className="inline-flex items-center text-sm text-red-600 hover:text-red-500"
                  >
                    <FaSignOutAlt className="mr-1.5" />
                    Sign out of all sessions
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'history' && (
            <div>
              <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
              <div className="overflow-hidden">
                <ul className="divide-y divide-gray-200">
                  <li className="py-4">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <FaFileAlt className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">Report Generated</p>
                          <p className="text-sm text-gray-500">Today</p>
                        </div>
                        <p className="text-sm text-gray-500">
                          You generated a new report: "Genetic Skin Analysis Report"
                        </p>
                      </div>
                    </div>
                  </li>
                  <li className="py-4">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <FaDna className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">Analysis Completed</p>
                          <p className="text-sm text-gray-500">Today</p>
                        </div>
                        <p className="text-sm text-gray-500">
                          Analysis of your DNA file was completed successfully
                        </p>
                      </div>
                    </div>
                  </li>
                  <li className="py-4">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                          <FaUpload className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">DNA File Uploaded</p>
                          <p className="text-sm text-gray-500">Today</p>
                        </div>
                        <p className="text-sm text-gray-500">
                          You uploaded a new DNA file: "23andMe_raw_data.txt"
                        </p>
                      </div>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AccountPage;