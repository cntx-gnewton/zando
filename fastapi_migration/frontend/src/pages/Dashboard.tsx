import React from 'react';
import { Link } from 'react-router-dom';
import { FaUpload, FaDna, FaFileAlt } from 'react-icons/fa';

const DashboardPage: React.FC = () => {
  return (
    <div className="py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quick actions card */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/upload"
              className="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex items-center"
            >
              <FaUpload className="mr-2 text-blue-500" />
              Upload New DNA File
            </Link>
            <Link
              to="/analysis"
              className="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex items-center"
            >
              <FaDna className="mr-2 text-blue-500" />
              View Analyses
            </Link>
            <Link
              to="/reports"
              className="block w-full text-left px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex items-center"
            >
              <FaFileAlt className="mr-2 text-blue-500" />
              View Reports
            </Link>
          </div>
        </div>
        
        {/* Recent activity card */}
        <div className="bg-white shadow rounded-lg p-6 md:col-span-2">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
          <div className="border-t border-gray-200 -mx-6 px-6">
            <div className="py-3 flex items-center border-b border-gray-200">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                <FaDna className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">Analysis completed</p>
                <p className="text-sm text-gray-500">Your DNA file was successfully analyzed</p>
              </div>
              <p className="text-sm text-gray-500">Just now</p>
            </div>
            <div className="py-3 flex items-center border-b border-gray-200">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                <FaFileAlt className="h-5 w-5 text-green-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">Report generated</p>
                <p className="text-sm text-gray-500">Your personalized report is ready to view</p>
              </div>
              <p className="text-sm text-gray-500">5 minutes ago</p>
            </div>
            <div className="py-3 flex items-center">
              <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                <FaUpload className="h-5 w-5 text-blue-600" />
              </div>
              <div className="ml-4 flex-1">
                <p className="text-sm font-medium text-gray-900">DNA file uploaded</p>
                <p className="text-sm text-gray-500">Your DNA file was successfully uploaded</p>
              </div>
              <p className="text-sm text-gray-500">10 minutes ago</p>
            </div>
          </div>
          <div className="mt-4 text-right">
            <Link to="/activity" className="text-sm font-medium text-blue-600 hover:text-blue-500">
              View all activity
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;