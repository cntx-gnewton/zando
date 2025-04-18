import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FileUpload, FileList, FormatInfo } from '../components/dna';
import { FaArrowRight, FaInfoCircle, FaDna } from 'react-icons/fa';
import { useAnalysis } from '../hooks/useAnalysis';

const UploadPage: React.FC = () => {
  const [showFormatInfo, setShowFormatInfo] = useState(false);
  const { currentAnalysis } = useAnalysis();
  
  const handleFileProcessed = (fileHash: string) => {
    console.log('File processed:', fileHash);
    // Could trigger a notification or other actions here
  };
  
  return (
    <div className="py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Upload DNA File</h1>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Upload Box */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Upload New DNA File</h2>
            <p className="text-gray-600 mb-4">
              Drag and drop your raw DNA data file below or click to browse. We accept files from 
              23andMe, AncestryDNA, and MyHeritage.
            </p>
            <FileUpload onFileProcessed={handleFileProcessed} />
          </div>
          
          {/* Previously Uploaded Files */}
          <div className="bg-white shadow rounded-lg p-6">
            <FileList onFileSelect={(fileHash, fileName) => console.log('Selected:', fileHash, fileName)} />
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Next Step Card */}
          {currentAnalysis?.fileHash && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-6 shadow-sm">
              <h2 className="text-lg font-medium text-gray-900 mb-2">Ready for Analysis</h2>
              <p className="text-gray-600 mb-4">
                Your DNA file <strong>{currentAnalysis.fileName}</strong> is ready for analysis.
              </p>
              
              {currentAnalysis.snpCount && (
                <div className="bg-white rounded p-3 mb-4 flex items-center text-sm">
                  <FaDna className="text-blue-500 mr-2" />
                  <span>
                    <strong>{currentAnalysis.snpCount.toLocaleString()}</strong> genetic markers detected
                  </span>
                </div>
              )}
              
              <Link 
                to="/analysis" 
                className="w-full block text-center bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition flex items-center justify-center"
                onClick={() => console.log("Proceeding to analysis with file hash:", currentAnalysis.fileHash)}
              >
                Proceed to Analysis
                <FaArrowRight className="ml-2" />
              </Link>
            </div>
          )}
          
          {/* Format Info Toggle */}
          <div className="bg-white shadow rounded-lg p-6">
            <button
              onClick={() => setShowFormatInfo(!showFormatInfo)}
              className="flex items-center text-blue-600 hover:text-blue-800"
            >
              <FaInfoCircle className="mr-2" />
              {showFormatInfo ? 'Hide format information' : 'Show supported file formats'}
            </button>
            
            {showFormatInfo && (
              <div className="mt-4">
                <FormatInfo />
              </div>
            )}
          </div>
          
          {/* Help Section */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Need Help?</h2>
            <div className="space-y-3">
              <p className="text-sm text-gray-600">
                If you're having trouble uploading your DNA file, please check our help guides:
              </p>
              <ul className="space-y-2 text-sm text-blue-600">
                <li>
                  <a href="#" className="hover:text-blue-800">How to export your 23andMe data</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-800">Downloading raw DNA from AncestryDNA</a>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-800">Troubleshooting common upload issues</a>
                </li>
              </ul>
              <p className="text-sm text-gray-600 mt-4">
                For further assistance, please contact our support team.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;