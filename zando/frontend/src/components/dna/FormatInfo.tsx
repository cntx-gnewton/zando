import React, { useState, useEffect } from 'react';
import { FaInfoCircle, FaSpinner, FaCheck, FaTimes } from 'react-icons/fa';
import { dnaApi } from '../../api/dnaApi';
import { FileFormat } from '../../types/dna';

type FormatInfoProps = {
  className?: string;
};

const FormatInfo: React.FC<FormatInfoProps> = ({ className = '' }) => {
  const [loading, setLoading] = useState(true);
  const [formats, setFormats] = useState<string[]>([]);
  const [formatDetails, setFormatDetails] = useState<Record<string, FileFormat>>({});
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    fetchFormatInfo();
  }, []);
  
  const fetchFormatInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await dnaApi.getSupportedFormats();
      
      setFormats(response.formats);
      setFormatDetails(response.details);
    } catch (err) {
      console.error('Error fetching format info:', err);
      setError('Failed to load format information');
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className={`flex justify-center items-center p-4 ${className}`}>
        <FaSpinner className="animate-spin mr-2 text-blue-500" />
        <span>Loading format information...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className={`text-center text-red-500 p-4 ${className}`}>
        <p>{error}</p>
        <button 
          onClick={fetchFormatInfo}
          className="mt-2 text-blue-500 hover:text-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }
  
  return (
    <div className={`bg-white rounded-lg shadow p-4 ${className}`}>
      <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
        <FaInfoCircle className="mr-2 text-blue-500" />
        Supported DNA File Formats
      </h3>
      
      <div className="space-y-4">
        {formats.map(format => {
          const details = formatDetails[format];
          if (!details) return null;
          
          return (
            <div key={format} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-900">{details.name}</h4>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  details.support_level === 'full'
                    ? 'bg-green-100 text-green-800'
                    : details.support_level === 'partial'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-blue-100 text-blue-800'
                }`}>
                  {details.support_level.toUpperCase()}
                </span>
              </div>
              
              <p className="text-sm text-gray-600 mb-3">{details.description}</p>
              
              <div className="text-xs text-gray-500">
                <p><strong>File pattern:</strong> {details.file_pattern}</p>
                <p className="mt-1"><strong>Example:</strong> <code className="bg-gray-100 p-1 rounded">{details.example_line}</code></p>
              </div>
              
              <div className="mt-3 pt-3 border-t border-gray-200">
                <h5 className="font-medium text-sm text-gray-900 mb-2">Requirements:</h5>
                <ul className="space-y-1">
                  <li className="flex items-center text-sm">
                    <FaCheck className="text-green-500 mr-1.5 flex-shrink-0" />
                    <span>Text file with tab or comma-separated values</span>
                  </li>
                  <li className="flex items-center text-sm">
                    <FaCheck className="text-green-500 mr-1.5 flex-shrink-0" />
                    <span>Contains SNP identifiers (rsIDs)</span>
                  </li>
                  <li className="flex items-center text-sm">
                    <FaCheck className="text-green-500 mr-1.5 flex-shrink-0" />
                    <span>Includes chromosome and position information</span>
                  </li>
                  <li className="flex items-center text-sm">
                    <FaCheck className="text-green-500 mr-1.5 flex-shrink-0" />
                    <span>Contains genotype information (alleles)</span>
                  </li>
                  {details.support_level !== 'full' && (
                    <li className="flex items-center text-sm">
                      <FaTimes className="text-red-500 mr-1.5 flex-shrink-0" />
                      <span>Some advanced features might not be available</span>
                    </li>
                  )}
                </ul>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 bg-blue-50 rounded-lg p-3 text-sm text-blue-700">
        <strong>Note:</strong> If you encounter issues with your DNA file, please ensure it's 
        the raw data export from your DNA testing service. The file should not be modified 
        or processed by any third-party tools.
      </div>
    </div>
  );
};

export default FormatInfo;