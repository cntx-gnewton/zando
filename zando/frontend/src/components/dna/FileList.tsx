import React, { useState, useEffect } from 'react';
import { FaFile, FaSpinner, FaTrash, FaInfoCircle, FaSearch } from 'react-icons/fa';
import { dnaApi } from '../../api/dnaApi';
import { DNAFileUploadResponse } from '../../types/dna';
import { useAnalysis } from '../../hooks/useAnalysis';
import { useNotification } from '../../hooks/useNotification';

type FileListProps = {
  onFileSelect?: (fileHash: string, fileName: string) => void;
};

const FileList: React.FC<FileListProps> = ({ onFileSelect }) => {
  const [files, setFiles] = useState<DNAFileUploadResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalFiles, setTotalFiles] = useState(0);
  const pageSize = 5;
  
  const { setCurrentAnalysis } = useAnalysis();
  const { showNotification } = useNotification();
  
  useEffect(() => {
    fetchFiles();
  }, [page]);
  
  const fetchFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, use the mock implementation in the API
      const offset = (page - 1) * pageSize;
      const response = await dnaApi.getUploadedFiles(pageSize, offset);
      
      setFiles(response.files);
      setTotalFiles(response.total);
    } catch (err) {
      console.error('Error fetching files:', err);
      setError('Failed to load DNA files');
      showNotification({
        type: 'error',
        message: 'Failed to load DNA files',
        details: err instanceof Error ? err.message : 'Unknown error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleDeleteFile = async (fileHash: string) => {
    // This would be implemented later with a confirmation dialog
    alert('File deletion is not implemented yet');
  };
  
  const handleFileSelect = (file: DNAFileUploadResponse) => {
    if (onFileSelect) {
      onFileSelect(file.file_hash, file.file_name);
    }
    
    setCurrentAnalysis({
      fileHash: file.file_hash,
      fileName: file.file_name,
      snpCount: file.snp_count,
      status: 'uploaded'
    });
    
    showNotification({
      type: 'info',
      message: 'DNA file selected',
      details: `Selected ${file.file_name} for analysis`
    });
  };
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  const filteredFiles = files.filter(file => 
    file.file_name.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const totalPages = Math.ceil(totalFiles / pageSize);
  
  if (loading && files.length === 0) {
    return (
      <div className="flex justify-center items-center p-8">
        <FaSpinner className="animate-spin mr-2 text-blue-500" />
        <span>Loading DNA files...</span>
      </div>
    );
  }
  
  if (error && files.length === 0) {
    return (
      <div className="text-center p-8 text-red-500">
        <p>{error}</p>
        <button 
          onClick={fetchFiles}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-4">
        <h2 className="text-lg font-medium text-gray-900 mb-2">Previously Uploaded Files</h2>
        <div className="flex items-center mb-4">
          <div className="relative flex-1">
            <input
              type="text"
              placeholder="Search files..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <FaSearch className="absolute left-3 top-3 text-gray-400" />
          </div>
        </div>
      </div>
      
      {filteredFiles.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded-lg">
          <FaFile className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No DNA files found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'No files match your search' : 'Upload your first DNA file to get started'}
          </p>
        </div>
      ) : (
        <div className="overflow-hidden border border-gray-200 rounded-lg">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  File Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date Uploaded
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Format
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFiles.map((file) => (
                <tr key={file.file_hash} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <FaFile className="text-blue-500 mr-2" />
                      <div className="text-sm font-medium text-gray-900 cursor-pointer hover:text-blue-600" onClick={() => handleFileSelect(file)}>
                        {file.file_name}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{formatDate(file.upload_date)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{formatFileSize(file.file_size)}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {file.format || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button 
                      onClick={() => handleFileSelect(file)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      title="Use this file"
                    >
                      <FaInfoCircle />
                    </button>
                    <button 
                      onClick={() => handleDeleteFile(file.file_hash)}
                      className="text-red-600 hover:text-red-900"
                      title="Delete file"
                    >
                      <FaTrash />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setPage(p => Math.max(p - 1, 1))}
                  disabled={page === 1}
                  className={`relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                    page === 1 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(p => Math.min(p + 1, totalPages))}
                  disabled={page === totalPages}
                  className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md ${
                    page === totalPages 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing <span className="font-medium">{(page - 1) * pageSize + 1}</span> to{' '}
                    <span className="font-medium">{Math.min(page * pageSize, totalFiles)}</span> of{' '}
                    <span className="font-medium">{totalFiles}</span> results
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button
                      onClick={() => setPage(p => Math.max(p - 1, 1))}
                      disabled={page === 1}
                      className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium ${
                        page === 1 
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                          : 'bg-white text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      <span className="sr-only">Previous</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                    
                    {/* Page numbers */}
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNum => (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                          page === pageNum
                            ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    ))}
                    
                    <button
                      onClick={() => setPage(p => Math.min(p + 1, totalPages))}
                      disabled={page === totalPages}
                      className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium ${
                        page === totalPages 
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                          : 'bg-white text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      <span className="sr-only">Next</span>
                      <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FileList;