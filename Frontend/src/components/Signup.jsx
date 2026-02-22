import { useState } from 'react';
import {
    TextInput,
    PasswordInput,
    Button,
    Form,
    Stack,
    Link,
} from '@carbon/react';
import { ArrowRight } from '@carbon/icons-react';
import './Login.css';

const Signup = ({ onNavigate, onLogin }) => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Signing up with:', name, email, password);
        onLogin();
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h2 className="auth-title">Create Account</h2>
                <p className="auth-subtitle">Join us to start planning smarter trips.</p>

                <Form onSubmit={handleSubmit} className="auth-form">
                    <Stack gap={5}>
                        <TextInput
                            id="signup-name"
                            labelText="Full Name"
                            placeholder="John Doe"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                        <TextInput
                            id="signup-email"
                            labelText="Email Address"
                            placeholder="you@example.com"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <PasswordInput
                            id="signup-password"
                            labelText="Password"
                            placeholder="Create a password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <Button type="submit" renderIcon={ArrowRight} className="auth-btn">
                            Sign Up
                        </Button>
                    </Stack>
                </Form>

                <div className="auth-footer">
                    Already have an account?{' '}
                    <button className="btn-link" onClick={() => onNavigate('login')}>Log in</button>
                </div>
            </div>
        </div>
    );
};

export default Signup;
