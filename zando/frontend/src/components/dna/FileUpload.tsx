import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { FaUpload, FaFile, FaSpinner, FaCheckCircle } from 'react-icons/fa';
import axios from 'axios';
import { dnaApi } from '../../api/dnaApi';
import { useAnalysis } from '../../hooks/useAnalysis';
import { useNotification } from '../../hooks/useNotification';
import { API_URL } from '../../config';

type FileUploadProps = {
  onFileProcessed?: (fileHash: string) => void;
};

const FileUpload: React.FC<FileUploadProps> = ({ onFileProcessed }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);
  const uploadTimeout = useRef<NodeJS.Timeout | null>(null);
  
  const { setCurrentAnalysis } = useAnalysis();
  const { showNotification } = useNotification();
  
  // Simulated progress to show during upload
  const simulateProgress = useCallback(() => {
    setUploadProgress(0);
    
    const intervalTime = 100;
    const increment = 3;
    const maxProgress = 90;
    
    const timer = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= maxProgress) {
          clearInterval(timer);
          return prev;
        }
        return prev + increment;
      });
    }, intervalTime);
    
    return timer;
  }, []);
  
  const uploadFile = useCallback(async (fileToUpload: File) => {
    try {
      setUploading(true);
      const progressTimer = simulateProgress();
      uploadTimeout.current = progressTimer;
      
      const response = await dnaApi.uploadFile(fileToUpload);
      
      clearInterval(progressTimer);
      setUploadProgress(100);
      setUploadComplete(true);
      
      showNotification({
        type: 'success',
        message: 'File successfully uploaded'
      });
      
      if (response.file_hash && onFileProcessed) {
        onFileProcessed(response.file_hash);
        
        // Store basic info about the current file in the analysis context
        setCurrentAnalysis({
          fileHash: response.file_hash,
          fileName: fileToUpload.name,
          snpCount: response.snp_count || 0,
          status: 'uploaded'
        });
      }
      
      return response;
    } catch (error) {
      clearInterval(uploadTimeout.current as NodeJS.Timeout);
      setUploadProgress(0);
      
      // Check if it's a network error (likely API connection issue)
      const isNetworkError = axios.isAxiosError(error) && !error.response;
      
      showNotification({
        type: 'error',
        message: isNetworkError ? 'API connection error' : 'Error uploading file',
        details: isNetworkError 
          ? `Could not connect to API at ${API_URL}. Please check your network connection.`
          : (error instanceof Error ? error.message : 'Unknown error')
      });
      
      throw error;
    } finally {
      setUploading(false);
    }
  }, [onFileProcessed, setCurrentAnalysis, showNotification, simulateProgress]);
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const newFile = acceptedFiles[0];
      setFile(newFile);
      
      // Reset states when new file is added
      setUploadComplete(false);
      setUploadProgress(0);
      
      // Automatically start uploading
      uploadFile(newFile);
    }
  }, [uploadFile]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt']
    },
    maxFiles: 1
  });
  
  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-300 hover:bg-gray-50'
        } ${uploadComplete ? 'bg-green-50 border-green-300' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="space-y-4">
          {!file ? (
            <>
              <FaUpload className="mx-auto text-4xl text-gray-400" />
              <p className="text-lg font-medium text-gray-700">
                {isDragActive
                  ? 'Drop your DNA file here...'
                  : 'Drag and drop your DNA file, or click to browse'}
              </p>
              <p className="text-sm text-gray-500">
                Supported formats: 23andMe and AncestryDNA text files (.txt)
              </p>
            </>
          ) : (
            <div className="flex flex-col items-center space-y-4">
              {uploading ? (
                <>
                  <FaSpinner className="animate-spin text-4xl text-blue-500" />
                  <p className="text-lg font-medium text-gray-700">Uploading file...</p>
                </>
              ) : uploadComplete ? (
                <>
                  <FaCheckCircle className="text-4xl text-green-500" />
                  <p className="text-lg font-medium text-gray-700">Upload complete!</p>
                </>
              ) : (
                <>
                  <FaFile className="text-4xl text-blue-500" />
                  <p className="text-lg font-medium text-gray-700">{file.name}</p>
                </>
              )}
              
              <div className="w-full max-w-md h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${uploadComplete ? 'bg-green-500' : 'bg-blue-500'} transition-all duration-300`}
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              
              <p className="text-sm text-gray-500">
                {uploadComplete
                  ? 'File uploaded successfully - ready for report generation'
                  : `${uploadProgress.toFixed(0)}% complete`}
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Info section */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-800">About DNA File Uploads</h3>
        <p className="mt-1 text-sm text-gray-600">
          Your DNA file is processed securely on our servers. We extract only the
          relevant genetic information for skincare analysis and do not store your
          raw genetic data.
        </p>
        
        {/* API Connection Indicator */}
        <div className="flex items-center mt-3 pt-3 border-t border-gray-200">
          <div className="w-3 h-3 rounded-full mr-2 bg-green-500"></div>
          <p className="text-xs text-gray-500">
            Connected to API: {process.env.REACT_APP_API_URL}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;