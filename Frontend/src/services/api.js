/**
 * API Service for communicating with the PlanIT Backend
 */

const API_BASE_URL = '/api'; // Using proxy to avoid CORS

// Helper for API calls
const fetchAPI = async (endpoint, options = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Call Failed (${endpoint}):`, error);
        throw error;
    }
};

/**
 * Session Management
 */
export const createSession = async (userId = null) => {
    return await fetchAPI('/session/create', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId }),
    });
};

export const getSessionHistory = async (sessionId) => {
    return await fetchAPI(`/session/${sessionId}/history`);
};

/**
 * Chat Interaction
 */
export const sendMessage = async (sessionId, message) => {
    return await fetchAPI(`/session/${sessionId}/chat`, {
        method: 'POST',
        body: JSON.stringify({ message }),
    });
};

/**
 * User Profile
 */
export const getUserProfile = async (userId) => {
    return await fetchAPI(`/user/profile/${userId}`);
};

export const updateUserProfile = async (userId, data) => {
    return await fetchAPI(`/user/profile/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
};

/**
 * Simple Health Check
 */
export const checkHealth = async () => {
    return await fetchAPI('/health');
};
