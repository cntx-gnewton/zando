import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

interface GoogleLoginComponentProps {
  onSuccess?: (credentialResponse: any) => void;
  onError?: () => void;
}

const GoogleLoginComponent: React.FC<GoogleLoginComponentProps> = ({ 
  onSuccess, 
  onError 
}) => {
  const navigate = useNavigate();

  const handleSuccess = (credentialResponse: any) => {
    console.log('Google login successful:', credentialResponse);
    
    // Store the token in localStorage
    localStorage.setItem('google_token', credentialResponse.credential);
    
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

  return (
    <div className="google-login-button">
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={handleError}
        useOneTap
        theme="outline"
        size="large"
        text="continue_with"
        shape="rectangular"
      />
    </div>
  );
};

export default GoogleLoginComponent;