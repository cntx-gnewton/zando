import React, { useState } from 'react';
import { FaUser, FaLock, FaHistory, FaFileAlt, FaSignOutAlt, FaDna, FaUpload, FaGoogle, FaFileMedical } from 'react-icons/fa';
import useAuth from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

const AccountPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'history'>('profile');
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Format the created date for display
  const createdDate = user?.createdAt 
    ? new Date(user.createdAt).toLocaleDateString() 
    : new Date().toLocaleDateString();
  
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
              <h2 className="text-lg font-medium text-gray-900 mb-4">Google Account Information</h2>
              
              {user?.picture && (
                <div className="flex items-center space-x-4 mb-6">
                  <img 
                    src={user.picture} 
                    alt={user.name} 
                    className="h-16 w-16 rounded-full"
                  />
                  <div>
                    <div className="text-xl font-medium text-gray-900">{user.name}</div>
                    <div className="text-sm text-gray-500 flex items-center mt-1">
                      <FaGoogle className="text-blue-500 mr-1" /> 
                      Google Account
                    </div>
                  </div>
                </div>
              )}
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    name="name"
                    id="name"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm bg-gray-50"
                    value={user?.name || ''}
                    readOnly
                    disabled
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    This name comes from your Google account
                  </p>
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm bg-gray-50"
                    value={user?.email || ''}
                    readOnly
                    disabled
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Email address from your Google account
                  </p>
                </div>
                <div>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <FaSignOutAlt className="mr-2" />
                    Sign Out
                  </button>
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Account Information</h2>
                <div className="bg-gray-50 rounded-md p-4">
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Member since</dt>
                      <dd className="mt-1 text-sm text-gray-900">{createdDate}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Account type</dt>
                      <dd className="mt-1 text-sm text-gray-900">Google Account</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Reports generated</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          0
                        </span>
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">DNA files</dt>
                      <dd className="mt-1 text-sm text-gray-900">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          0
                        </span>
                      </dd>
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
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <FaGoogle className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-medium text-blue-800">Google Authentication</h3>
                    <div className="mt-2 text-blue-700">
                      <p>Your account uses Google Authentication for secure sign-in.</p>
                      <p className="mt-1">With Google Authentication, you don't need to manage a separate password for this application.</p>
                    </div>
                  </div>
                </div>
              </div>

              <h2 className="text-lg font-medium text-gray-900 mb-4">Authentication Method</h2>
              <div className="bg-white border border-gray-200 rounded-md shadow-sm">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    <FaGoogle className="h-8 w-8 text-blue-500" />
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-gray-900">Google Account</h3>
                      <p className="text-sm text-gray-500">
                        You are signed in with your Google account ({user?.email})
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Current Session</h2>
                <div className="space-y-3">
                  <div className="bg-green-50 border border-green-100 rounded-md p-4 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">Active Google Session</p>
                      <p className="text-sm text-gray-500">Signed in with Google Authentication</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      Active
                    </span>
                  </div>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="inline-flex items-center text-sm text-red-600 hover:text-red-500"
                  >
                    <FaSignOutAlt className="mr-1.5" />
                    Sign out
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
                          <FaGoogle className="h-5 w-5 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">Account Created / Sign In</p>
                          <p className="text-sm text-gray-500">{createdDate}</p>
                        </div>
                        <p className="text-sm text-gray-500">
                          You connected your Google account to Cosnetix Genomics
                        </p>
                      </div>
                    </div>
                  </li>
                  
                  {/* Empty state when no activity yet */}
                  <div className="py-8 text-center text-gray-500">
                    <div className="inline-block p-4 rounded-full bg-gray-100 mb-4">
                      <FaFileAlt className="h-8 w-8 text-gray-400" />
                    </div>
                    <p className="text-lg font-medium mb-2">No activity yet</p>
                    <p className="text-sm max-w-md mx-auto">
                      Your activities like generating reports and uploading DNA files will appear here.
                    </p>
                    <div className="mt-4">
                      <Link 
                        to="/report" 
                        className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-800"
                      >
                        <FaFileMedical className="mr-2" />
                        Generate your first report
                      </Link>
                    </div>
                  </div>
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