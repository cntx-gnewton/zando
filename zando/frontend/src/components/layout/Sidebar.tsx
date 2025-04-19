import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  FaHome, 
  FaFileAlt, 
  FaUser,
  FaTachometerAlt,
  FaFileMedical
} from 'react-icons/fa';
import useAuth from '../../hooks/useAuth';

const Sidebar: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  // Public navigation items
  const publicNavigation = [
    { name: 'Home', to: '/', icon: FaHome },
  ];
  
  // Protected navigation items (only for authenticated users)
  const protectedNavigation = [
    { name: 'Generate Report', to: '/report', icon: FaFileMedical },
    { name: 'My Reports', to: '/reports', icon: FaFileAlt },
    { name: 'Account', to: '/account', icon: FaUser },
  ];
  
  // Combine the navigation items based on authentication state
  const navigation = isAuthenticated 
    ? [...publicNavigation, ...protectedNavigation]
    : publicNavigation;
  
  return (
    <div className="hidden md:flex md:flex-shrink-0">
      <div className="flex flex-col w-64">
        <div className="flex flex-col h-0 flex-1 border-r border-gray-200 bg-white">
          <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
            <nav className="mt-5 flex-1 px-2 bg-white space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.to}
                  className={({ isActive }) => 
                    `group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      isActive
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <item.icon 
                        className={`mr-3 flex-shrink-0 h-5 w-5 ${
                          isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                        }`}
                      />
                      {item.name}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;