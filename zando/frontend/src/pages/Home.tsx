import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaFileMedical, FaDna, FaFileAlt, FaUser } from 'react-icons/fa';
import { GoogleLogin } from "@react-oauth/google";
import useAuth from '../hooks/useAuth';

const HomePage: React.FC = () => {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  const handleLoginSuccess = (credentialResponse: any) => {
    console.log('Google login successful:', credentialResponse);
    login(credentialResponse.credential);
    
    // Navigate to report page after login
    navigate('/report');
  };

  return (
    <div className="py-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
            Understand Your Genetic Skin Profile
          </h1>
          <p className="mt-5 max-w-xl mx-auto text-xl text-gray-500">
            Upload your DNA data to discover personalized skincare recommendations based on your unique genetic makeup.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center space-y-4">
            <div className="space-y-4">
              <div className="text-center mb-2">
                <p className="text-gray-600 mb-4">Sign in to access exclusive features:</p>
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={handleLoginSuccess}
                    onError={() => console.log('Login Failed')}
                    useOneTap
                    theme="outline"
                    text="continue_with"
                    shape="rectangular"
                  />
                </div>
              </div>
              <div className="mt-4 text-center">
                <p className="text-blue-600 font-semibold">Sign in to:</p>
                <ul className="mt-2 text-gray-600">
                  <li>• Generate personalized reports</li>
                  <li>• Access your dashboard</li>
                  <li>• View past analysis results</li>
                  <li>• Manage your account</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Feature section */}
        <div className="py-12 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:text-center">
              <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">How It Works</h2>
              <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
                Personalized Genomic Analysis
              </p>
              <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
                Three simple steps to discover how your genes influence your skin's health and appearance.
              </p>
            </div>

            <div className="mt-10">
              <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-3 md:gap-8">
                <div className="text-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white mx-auto">
                    <FaFileMedical className="h-8 w-8" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">Generate Report</h3>
                  <p className="mt-2 text-base text-gray-500">
                    Simply upload your raw DNA data from 23andMe, Ancestry, or other genetic testing services.
                  </p>
                </div>

                <div className="text-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white mx-auto">
                    <FaDna className="h-8 w-8" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">Analyze Your Genetics</h3>
                  <p className="mt-2 text-base text-gray-500">
                    Our technology analyzes thousands of genetic markers related to skin health and characteristics.
                  </p>
                </div>

                <div className="text-center">
                  <div className="flex items-center justify-center h-16 w-16 rounded-md bg-blue-500 text-white mx-auto">
                    <FaFileAlt className="h-8 w-8" />
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-gray-900">Get Personalized Reports</h3>
                  <p className="mt-2 text-base text-gray-500">
                    Receive a comprehensive report with personalized skincare ingredient recommendations.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* CTA section */}
        <div className="bg-blue-50 rounded-lg shadow-sm mt-12">
          <div className="max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-extrabold text-gray-900">
              Ready to discover your genetic skin profile?
            </h2>
            <p className="mt-4 text-lg text-gray-500">
              Your DNA holds the keys to understanding your skin's unique needs. 
              Sign in today to get personalized skincare recommendations.
            </p>
            <div className="mt-8">
              {isAuthenticated ? (
                <Link
                  to="/report"
                  className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  Generate Your Report
                </Link>
              ) : (
                <div className="flex justify-center">
                  <GoogleLogin
                    onSuccess={handleLoginSuccess}
                    onError={() => console.log('Login Failed')}
                    useOneTap={false}
                    theme="outline"
                    text="signin_with"
                    shape="rectangular"
                    size="large"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;