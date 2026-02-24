import { useState } from 'react';
import {
    TextInput,
    PasswordInput,
    Button,
    Form,
    Stack,
    Checkbox,
    Link,
    InlineNotification,
} from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import { signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../firebase';
import { loginUser, googleLogin } from '../services/api';
import './Login.css';

const Login = ({ onNavigate, onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const data = await loginUser(email, password);
            onLogin(data.user);
        } catch (err) {
            setError(err.message || 'Invalid email or password.');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setError('');
        setLoading(true);

        try {
            const result = await signInWithPopup(auth, googleProvider);
            const { displayName, email: gEmail } = result.user;

            // Sync with our MongoDB backend
            const data = await googleLogin(displayName || '', gEmail);
            onLogin(data.user);
        } catch (err) {
            if (err.code !== 'auth/popup-closed-by-user') {
                setError(err.message || 'Google sign-in failed.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h2 className="auth-title">Welcome Back</h2>
                <p className="auth-subtitle">Log in to continue planning your journey.</p>

                {error && (
                    <InlineNotification
                        kind="error"
                        title="Login failed"
                        subtitle={error}
                        lowContrast
                        hideCloseButton
                        className="auth-error"
                    />
                )}

                <Form onSubmit={handleSubmit} className="auth-form">
                    <Stack gap={5}>
                        <TextInput
                            id="login-email"
                            labelText="Email Address"
                            placeholder="you@example.com"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <PasswordInput
                            id="login-password"
                            labelText="Password"
                            placeholder="Enter your password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <div className="auth-options">
                            <Checkbox id="remember-me" labelText="Remember me" />
                            <Link href="#" size="sm">Forgot password?</Link>
                        </div>
                        <Button
                            type="submit"
                            renderIcon={ArrowRight}
                            className="auth-btn"
                            disabled={loading}
                        >
                            {loading ? 'Logging in…' : 'Log In'}
                        </Button>
                    </Stack>
                </Form>

                <div className="auth-divider">
                    <span>or</span>
                </div>

                <button
                    className="google-btn"
                    onClick={handleGoogleLogin}
                    disabled={loading}
                    type="button"
                >
                    <svg className="google-icon" viewBox="0 0 24 24" width="20" height="20">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    Continue with Google
                </button>

                <div className="auth-footer">
                    Don't have an account?{' '}
                    <button className="btn-link" onClick={() => onNavigate('signup')}>Sign up</button>
                </div>
            </div>
        </div>
    );
};

export default Login;
