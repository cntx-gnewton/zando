import React, { useContext, useEffect } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';

interface GoogleLoginComponentProps {
  onSuccess?: (credentialResponse: any) => void;
  onError?: () => void;
}

const GoogleLoginComponent: React.FC<GoogleLoginComponentProps> = ({ 
  onSuccess, 
  onError 
}) => {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useContext(AuthContext);

  // If user is already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const handleSuccess = (credentialResponse: any) => {
    console.log('Google login successful:', credentialResponse);
    
    // Store the token in localStorage and update auth context
    login(credentialResponse.credential);
    
    // Call the onSuccess callback if provided
    if (onSuccess) {
      onSuccess(credentialResponse);
    } else {
      // Default behavior - navigate to dashboard
      navigate('/dashboard');
    }
  };

  const handleError = () => {
    console.error('Login Failed');
    
    // Call the onError callback if provided
    if (onError) {
      onError();
    }
  };

  // Don't render login button if already authenticated
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="google-login-button">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={handleError}
        useOneTap={false}
        theme="outline"
        size="large"
        text="continue_with"
        shape="rectangular"
      />
    </div>
  );
};

export default GoogleLoginComponent;