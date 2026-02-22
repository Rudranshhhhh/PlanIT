import { useState } from 'react';
import {
    TextInput,
    PasswordInput,
    Button,
    Form,
    Stack,
    Checkbox,
    Link,
} from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import './Login.css';

const Login = ({ onNavigate, onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Logging in with:', email, password);
        onLogin();
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h2 className="auth-title">Welcome Back</h2>
                <p className="auth-subtitle">Log in to continue planning your journey.</p>

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
                        <Button type="submit" renderIcon={ArrowRight} className="auth-btn">
                            Log In
                        </Button>
                    </Stack>
                </Form>

                <div className="auth-footer">
                    Don't have an account?{' '}
                    <button className="btn-link" onClick={() => onNavigate('signup')}>Sign up</button>
                </div>
            </div>
        </div>
    );
};

export default Login;
