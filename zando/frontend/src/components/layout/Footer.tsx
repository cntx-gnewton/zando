import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex justify-center md:justify-start space-x-6">
            <Link to="/privacy" className="text-gray-500 hover:text-gray-600">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-gray-500 hover:text-gray-600">
              Terms of Service
            </Link>
            <Link to="/contact" className="text-gray-500 hover:text-gray-600">
              Contact Us
            </Link>
          </div>
          <div className="mt-4 md:mt-0">
            <p className="text-center md:text-left text-gray-400 text-sm">
              &copy; {new Date().getFullYear()} Cosnetix Genomics. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;