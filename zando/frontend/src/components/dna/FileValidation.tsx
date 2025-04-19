import React, { useState, useEffect } from 'react';
import { FaCheckCircle, FaExclamationCircle, FaSpinner, FaDna, FaChartBar } from 'react-icons/fa';
import { dnaApi } from '../../api/dnaApi';

type FileValidationProps = {
  file: File;
  onValidated?: (isValid: boolean, stats: any) => void;
  className?: string;
};

const FileValidation: React.FC<FileValidationProps> = ({ file, onValidated, className = '' }) => {
  const [loading, setLoading] = useState(true);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    validateFile();
  }, [file]);
  
  const validateFile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await dnaApi.validateFile(file);
      
      setValidationResult(result);
      
      if (onValidated) {
        onValidated(result.valid, result.stats);
      }
    } catch (err) {
      console.error('Error validating file:', err);
      setError('Failed to validate DNA file');
      
      if (onValidated) {
        onValidated(false, null);
      }
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className={`flex justify-center items-center p-6 ${className}`}>
        <FaSpinner className="animate-spin mr-2 text-blue-500" />
        <span>Validating your DNA file...</span>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className={`bg-red-50 rounded-lg p-6 ${className}`}>
        <div className="flex items-start">
          <FaExclamationCircle className="text-red-500 mt-0.5 mr-2" />
          <div>
            <h3 className="font-medium text-red-800">Validation Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button 
              onClick={validateFile}
              className="mt-3 text-sm text-blue-600 hover:text-blue-800"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (!validationResult?.valid) {
    return (
      <div className={`bg-red-50 rounded-lg p-6 ${className}`}>
        <div className="flex items-start">
          <FaExclamationCircle className="text-red-500 mt-0.5 mr-2" />
          <div>
            <h3 className="font-medium text-red-800">Invalid DNA File</h3>
            <p className="text-sm text-red-700 mt-1">
              The file appears to be invalid or in an unsupported format. Please ensure you're uploading
              raw DNA data from a supported provider.
            </p>
            {validationResult?.message && (
              <p className="text-sm text-red-700 mt-2">{validationResult.message}</p>
            )}
          </div>
        </div>
      </div>
    );
  }
  
  // Valid file
  return (
    <div className={`bg-green-50 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <FaCheckCircle className="text-green-500 mt-0.5 mr-2 text-xl" />
        <div>
          <h3 className="font-medium text-green-800">Valid DNA File</h3>
          <p className="text-sm text-green-700 mt-1">
            Your DNA file has been validated and is ready for processing.
          </p>
          
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-3 flex items-center">
              <FaDna className="text-blue-500 mr-2" />
              <div className="text-sm">
                <p className="text-gray-500">SNPs</p>
                <p className="font-medium text-gray-900">
                  {validationResult?.stats?.valid_snps?.toLocaleString() || 'N/A'}
                </p>
              </div>
            </div>
            <div className="bg-white rounded-lg p-3 flex items-center">
              <FaChartBar className="text-blue-500 mr-2" />
              <div className="text-sm">
                <p className="text-gray-500">Format</p>
                <p className="font-medium text-gray-900">
                  {validationResult?.format || 'Unknown'}
                </p>
              </div>
            </div>
          </div>
          
          {validationResult?.stats?.chromosomes && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-green-800 mb-2">Chromosomes Detected</h4>
              <div className="flex flex-wrap gap-2">
                {validationResult.stats.chromosomes.map((chr: string) => (
                  <span 
                    key={chr}
                    className="px-2 py-1 text-xs font-medium bg-white rounded-md text-gray-700"
                  >
                    {chr}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {validationResult?.stats?.invalid_lines > 0 && (
            <div className="mt-4 bg-yellow-50 p-3 rounded-md text-sm text-yellow-800">
              <p className="font-medium">Note:</p>
              <p>{validationResult.stats.invalid_lines} invalid lines were detected but will be skipped during processing.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileValidation;