import React, { useState } from 'react';
import { useHistory } from '@docusaurus/router';
import { useAuth } from '../contexts/AuthContext';

function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    programmingLevel: 'beginner',
    roboticsFamiliarity: 'none',
    learningGoal: 'personalInterest',
    timeCommitment: 'fewHours',
    priorExperience: 'none'
  });
  const [error, setError] = useState('');
  const history = useHistory();
  const { register } = useAuth();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const [isRegistered, setIsRegistered] = useState(false);

  const handleRegister = async (e) => {
    e.preventDefault();

    // Prepare user data for registration
    const userData = {
      name: formData.name,
      email: formData.email,
      password: formData.password, // Note: In a real app, password would be handled securely
      programmingLevel: formData.programmingLevel,
      roboticsFamiliarity: formData.roboticsFamiliarity,
      learningGoal: formData.learningGoal,
      timeCommitment: formData.timeCommitment,
      priorExperience: formData.priorExperience
    };

    try {
      // Call the register function from auth context
      const result = await register(userData);

      // Show welcome message instead of redirecting immediately
      setIsRegistered(true);
    } catch (err) {
      setError('Registration failed. Please try again.');
    }
  };

  if (isRegistered) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        padding: '2rem 1rem'
      }}>
        <div style={{
          width: '100%',
          maxWidth: '500px',
          margin: '0 auto'
        }}>
          <div style={{
            textAlign: 'center',
            marginBottom: '2rem'
          }}>
            <h1 style={{
              fontSize: '2rem',
              color: '#333',
              marginBottom: '0.5rem'
            }}>
              Physical AI & Humanoid Robotics
            </h1>
            <p style={{
              color: '#666',
              fontSize: '1rem'
            }}>
              Welcome to the textbook
            </p>
          </div>

          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            padding: '2rem',
            textAlign: 'center'
          }}>
            <div style={{ marginBottom: '1rem' }}>
              <img
                src="/img/celebrate.png"
                alt="Celebration"
                style={{
                  width: '120px',
                  height: '120px',
                  objectFit: 'contain',
                  margin: '0 auto',
                  display: 'block'
                }}
              />
            </div>
            <h2 style={{
              margin: '0 0 1rem 0',
              fontSize: '1.5rem',
              color: '#333'
            }}>
              Welcome, {formData.name}!
            </h2>
            <p style={{
              marginBottom: '1.5rem',
              color: '#666',
              lineHeight: '1.6'
            }}>
              Your account has been successfully created. You're now ready to start your journey in Physical AI and Robotics!
            </p>

            <div style={{ marginBottom: '1.5rem' }}>
              <a
                href="/"
                style={{
                  display: 'inline-block',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#FF00FF',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '4px',
                  fontSize: '1rem',
                  fontWeight: '500'
                }}
                className="button button--primary button--lg"
              >
                Start Learning
              </a>
            </div>

            <div style={{
              marginTop: '1.5rem',
              paddingTop: '1.5rem',
              borderTop: '1px solid #eee'
            }}>
              <p style={{
                margin: '0 0 1rem 0',
                color: '#666',
                fontSize: '0.9rem'
              }}>
                Or continue to explore:
              </p>
              <div style={{
                display: 'flex',
                gap: '0.5rem',
                justifyContent: 'center'
              }}>
                <a
                  href="/docs/chapter-1/intro"
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#f0f0f0',
                    color: '#333',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    fontSize: '0.85rem'
                  }}
                  className="button button--secondary button--sm"
                >
                  Textbook
                </a>
                <a
                  href="/author"
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#f0f0f0',
                    color: '#333',
                    textDecoration: 'none',
                    borderRadius: '4px',
                    fontSize: '0.85rem'
                  }}
                  className="button button--secondary button--sm"
                >
                  About Author
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      padding: '2rem 1rem'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '600px',
        margin: '0 auto'
      }}>
        <div style={{
          textAlign: 'center',
          marginBottom: '2rem'
        }}>
          <h1 style={{
            fontSize: '2rem',
            color: '#333',
            marginBottom: '0.5rem'
          }}>
            Physical AI & Humanoid Robotics
          </h1>
          <p style={{
            color: '#666',
            fontSize: '1rem'
          }}>
            Create your account
          </p>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          padding: '2rem'
        }}>
          <div style={{
            textAlign: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{
              margin: '0 0 0.5rem 0',
              fontSize: '1.5rem',
              color: '#333'
            }}>
              Create Your Account
            </h2>
            <p style={{
              margin: 0,
              color: '#666',
              fontSize: '0.9rem'
            }}>
              Tell us about your background to personalize your learning experience
            </p>
          </div>

          {error && (
            <div style={{
              backgroundColor: '#fee',
              color: '#c33',
              padding: '0.75rem',
              borderRadius: '4px',
              marginBottom: '1rem',
              border: '1px solid #fcc'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleRegister}>
            <div style={{ marginBottom: '1.25rem' }}>
              <label htmlFor="name" style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '1rem'
                }}
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label htmlFor="email" style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '1rem'
                }}
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label htmlFor="password" style={{
                display: 'block',
                marginBottom: '0.5rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '1rem'
                }}
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Programming Level
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['beginner', 'intermediate', 'advanced'].map((level) => (
                  <label key={level} style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: formData.programmingLevel === level ? '2px solid #FF00FF' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: formData.programmingLevel === level ? '#fff0ff' : 'white'
                  }}>
                    <input
                      type="radio"
                      name="programmingLevel"
                      value={level}
                      checked={formData.programmingLevel === level}
                      onChange={handleChange}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span>{level.charAt(0).toUpperCase() + level.slice(1)}</span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Robotics Familiarity
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['none', 'basic', 'intermediate', 'advanced'].map((level) => (
                  <label key={level} style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: formData.roboticsFamiliarity === level ? '2px solid #FF00FF' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: formData.roboticsFamiliarity === level ? '#fff0ff' : 'white'
                  }}>
                    <input
                      type="radio"
                      name="roboticsFamiliarity"
                      value={level}
                      checked={formData.roboticsFamiliarity === level}
                      onChange={handleChange}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span>
                      {level === 'none' ? 'No Experience' :
                       level === 'basic' ? 'Basic Knowledge' :
                       level.charAt(0).toUpperCase() + level.slice(1)}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Learning Goal
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['personalInterest', 'academic', 'professional', 'hobby'].map((goal) => (
                  <label key={goal} style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: formData.learningGoal === goal ? '2px solid #FF00FF' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: formData.learningGoal === goal ? '#fff0ff' : 'white'
                  }}>
                    <input
                      type="radio"
                      name="learningGoal"
                      value={goal}
                      checked={formData.learningGoal === goal}
                      onChange={handleChange}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span>
                      {goal === 'personalInterest' ? 'Personal Interest' :
                       goal === 'academic' ? 'Academic Study' :
                       goal === 'professional' ? 'Professional Development' :
                       'For Fun/Hobby'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Time Commitment
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['fewHours', 'oneHour', 'fewTimes', 'daily'].map((time) => (
                  <label key={time} style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: formData.timeCommitment === time ? '2px solid #FF00FF' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: formData.timeCommitment === time ? '#fff0ff' : 'white'
                  }}>
                    <input
                      type="radio"
                      name="timeCommitment"
                      value={time}
                      checked={formData.timeCommitment === time}
                      onChange={handleChange}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span>
                      {time === 'fewHours' ? 'A few hours a week' :
                       time === 'oneHour' ? '1 hour daily' :
                       time === 'fewTimes' ? 'A few times a week' :
                       'Daily'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label className="form-label" style={{
                display: 'block',
                marginBottom: '0.75rem',
                fontWeight: '500',
                color: '#333'
              }}>
                Prior Experience
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['none', 'basic', 'some', 'extensive'].map((exp) => (
                  <label key={exp} style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0.5rem',
                    border: formData.priorExperience === exp ? '2px solid #FF00FF' : '1px solid #ddd',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    backgroundColor: formData.priorExperience === exp ? '#fff0ff' : 'white'
                  }}>
                    <input
                      type="radio"
                      name="priorExperience"
                      value={exp}
                      checked={formData.priorExperience === exp}
                      onChange={handleChange}
                      style={{ marginRight: '0.5rem' }}
                    />
                    <span>
                      {exp === 'none' ? 'No Prior Experience' :
                       exp === 'basic' ? 'Basic Experience' :
                       exp === 'some' ? 'Some Experience' :
                       'Extensive Experience'}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              style={{
                width: '100%',
                padding: '0.75rem',
                backgroundColor: '#FF00FF',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '1rem',
                cursor: 'pointer',
                fontWeight: '500'
              }}
              className="button button--primary"
            >
              Create Account
            </button>
          </form>

          <div style={{
            textAlign: 'center',
            marginTop: '1.5rem',
            paddingTop: '1.5rem',
            borderTop: '1px solid #eee'
          }}>
            <p style={{
              margin: 0,
              color: '#666'
            }}>
              Already have an account? <a href="/login" style={{ color: '#FF00FF' }}>Login here</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;