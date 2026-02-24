import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
    apiKey: "AIzaSyBGV5udp9_40cV8LZhqcH_I6XZflUTO918",
    authDomain: "plan-it-cd4df.firebaseapp.com",
    projectId: "plan-it-cd4df",
    storageBucket: "plan-it-cd4df.firebasestorage.app",
    messagingSenderId: "510161097193",
    appId: "1:510161097193:web:8ad8b9bd21226cea45bb78",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
