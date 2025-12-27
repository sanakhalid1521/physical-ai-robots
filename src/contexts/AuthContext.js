import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on component mount
    const checkAuthStatus = () => {
      const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
      const userEmail = localStorage.getItem('userEmail');
      const userProfile = localStorage.getItem('userProfile');

      if (isLoggedIn && userEmail) {
        const user = {
          email: userEmail,
          profile: userProfile ? JSON.parse(userProfile) : null
        };
        setCurrentUser(user);
      }
      setLoading(false);
    };

    checkAuthStatus();
  }, []);

  const login = async (email, password) => {
    try {
      // Use appropriate backend URL based on environment
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? 'https://sanakhalid123-physicalairag.hf.space'  // Your Hugging Face deployment
        : 'http://localhost:8000';  // Local development

      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();

      // Store authentication token and user info
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userEmail', data.user.email);
      if (data.user.profile) {
        localStorage.setItem('userProfile', JSON.stringify(data.user.profile));
      }

      const user = {
        email: data.user.email,
        profile: data.user.profile || null
      };
      setCurrentUser(user);
      return user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      // Use appropriate backend URL based on environment
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? 'https://sanakhalid123-physicalairag.hf.space'  // Your Hugging Face deployment
        : 'http://localhost:8000';  // Local development

      const response = await fetch(`${backendUrl}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data = await response.json();

      // Store authentication token and user info
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userEmail', data.user.email);
      if (data.user.profile) {
        localStorage.setItem('userProfile', JSON.stringify(data.user.profile));
      }

      const user = {
        email: data.user.email,
        profile: data.user.profile || null
      };
      setCurrentUser(user);
      return user;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      // Use appropriate backend URL based on environment
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? 'https://sanakhalid123-physicalairag.hf.space'  // Your Hugging Face deployment
        : 'http://localhost:8000';  // Local development

      // Make API call to backend logout endpoint
      await fetch(`${backendUrl}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with local logout even if backend call fails
    } finally {
      // Clear local storage and state
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('userProfile');
      setCurrentUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    if (!currentUser) return;

    try {
      // Use appropriate backend URL based on environment
      const backendUrl = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? 'https://sanakhalid123-physicalairag.hf.space'  // Your Hugging Face deployment
        : 'http://localhost:8000';  // Local development

      const response = await fetch(`${backendUrl}/api/auth/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        throw new Error('Profile update failed');
      }

      const data = await response.json();

      // Update local storage and state
      const updatedProfile = { ...currentUser.profile, ...data.user.profile };
      localStorage.setItem('userProfile', JSON.stringify(updatedProfile));

      const updatedUser = {
        ...currentUser,
        profile: updatedProfile
      };
      setCurrentUser(updatedUser);
      return updatedUser;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  };

  const value = {
    currentUser,
    login,
    register,
    logout,
    updateProfile,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}