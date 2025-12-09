// ========================================
// Configuration
// ========================================
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
    TOKEN_KEY: 'auth_token',
    USER_KEY: 'user_data'
};

// ========================================
// API Service Class
// ========================================
class APIService {
    static getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (includeAuth) {
            const token = localStorage.getItem(CONFIG.TOKEN_KEY);
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }
        
        return headers;
    }

    static async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
                ...options,
                headers: this.getHeaders(options.auth !== false)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // ========================================
    // Auth APIs
    // ========================================
    static async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
            auth: false
        });
    }

    static async login(email, password) {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${CONFIG.API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Login failed');
        
        return data;
    }

    static async getMe() {
        return this.request('/auth/me');
    }

    // ========================================
    // Doctor APIs
    // ========================================
    static async getDoctors() {
        return this.request('/doctors/');
    }

    static async getDoctor(id) {
        return this.request(`/doctors/${id}`);
    }

    static async getAllDoctors() {
        return this.request('/doctors/all');
    }

    static async createDoctor(doctorData) {
        return this.request('/doctors/', {
            method: 'POST',
            body: JSON.stringify(doctorData)
        });
    }

    static async deleteDoctor(id) {
        return this.request(`/doctors/${id}`, {
            method: 'DELETE'
        });
    }

    static async addSchedule(doctorId, scheduleData) {
        return this.request(`/doctors/${doctorId}/schedule`, {
            method: 'POST',
            body: JSON.stringify(scheduleData)
        });
    }

    static async deleteSchedule(scheduleId) {
        return this.request(`/doctors/schedules/${scheduleId}`, {
            method: 'DELETE'
        });
    }

    // ========================================
    // Appointment APIs
    // ========================================
    static async bookAppointment(appointmentData) {
        return this.request('/appointments/', {
            method: 'POST',
            body: JSON.stringify(appointmentData)
        });
    }

    static async getMyAppointments() {
        return this.request('/appointments/me');
    }

    static async getDoctorAppointments(doctorId) {
        return this.request(`/appointments/doctor/${doctorId}`);
    }

    static async getAllAppointments() {
        return this.request('/appointments/all');
    }

    static async cancelAppointment(id) {
        return this.request(`/appointments/${id}`, {
            method: 'DELETE'
        });
    }
}

// ========================================
// Authentication Helper
// ========================================
class AuthHelper {
    static saveToken(token) {
        localStorage.setItem(CONFIG.TOKEN_KEY, token);
    }

    static saveUser(user) {
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    }

    static getToken() {
        return localStorage.getItem(CONFIG.TOKEN_KEY);
    }

    static getUser() {
        const user = localStorage.getItem(CONFIG.USER_KEY);
        return user ? JSON.parse(user) : null;
    }

    static isAuthenticated() {
        return !!this.getToken();
    }

    static isAdmin() {
        const user = this.getUser();
        return user && user.role === 'ADMIN';
    }

    static logout() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
        window.location.href = '/login.html';
    }

    static requireAuth() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }

    static requireAdmin() {
        if (!this.isAuthenticated() || !this.isAdmin()) {
            window.location.href = '/index.html';
            return false;
        }
        return true;
    }
}

// ========================================
// Utility Functions
// ========================================
const Utils = {
    // Show notification toast
    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 transition-opacity ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    // Format date to readable string
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Format time to readable string
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Format full date and time
    formatDateTime(dateString) {
        return `${this.formatDate(dateString)} at ${this.formatTime(dateString)}`;
    },

    // Generate time slots based on start, end, and duration
    generateTimeSlots(startTime, endTime, duration = 60) {
        const slots = [];
        const start = new Date(`2000-01-01T${startTime}`);
        const end = new Date(`2000-01-01T${endTime}`);

        while (start < end) {
            const timeStr = start.toTimeString().slice(0, 5);
            slots.push(timeStr);
            start.setMinutes(start.getMinutes() + duration);
        }

        return slots;
    },

    // Get day name from day number (0-6)
    getDayName(dayNumber) {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return days[dayNumber];
    },

    // Validate email format
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Show loading spinner
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p class="text-gray-600 mt-4">Loading...</p>
                </div>
            `;
        }
    },

    // Hide loading spinner
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    },

    // Debounce function for search inputs
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Handle API errors gracefully
    handleError(error, customMessage = null) {
        console.error('Error:', error);
        const message = customMessage || error.message || 'An error occurred';
        this.showNotification(message, 'error');
    }
};

// ========================================
// Navigation Helper
// ========================================
class NavigationHelper {
    static updateNavbar() {
        const token = AuthHelper.getToken();
        const user = AuthHelper.getUser();
        const navButtons = document.getElementById('navButtons');
        
        if (!navButtons) return;

        if (token && user) {
            navButtons.innerHTML = `
                <a href="/doctors.html" class="text-gray-700 hover:text-blue-600">Doctors</a>
                <a href="${user.role === 'ADMIN' ? '/admin/dashboard.html' : '/appointments.html'}" 
                   class="text-gray-700 hover:text-blue-600">
                    ${user.role === 'ADMIN' ? 'Dashboard' : 'My Appointments'}
                </a>
                <button onclick="AuthHelper.logout()" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700">
                    Logout
                </button>
            `;
        } else {
            navButtons.innerHTML = `
                <a href="/login.html" class="text-gray-700 hover:text-blue-600">Login</a>
                <a href="/register.html" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">Register</a>
            `;
        }
    }
}

// ========================================
// Form Validation Helper
// ========================================
class FormValidator {
    static validateRequired(value, fieldName) {
        if (!value || value.trim() === '') {
            throw new Error(`${fieldName} is required`);
        }
        return true;
    }

    static validateEmail(email) {
        if (!Utils.isValidEmail(email)) {
            throw new Error('Please enter a valid email address');
        }
        return true;
    }

    static validatePassword(password, minLength = 6) {
        if (password.length < minLength) {
            throw new Error(`Password must be at least ${minLength} characters long`);
        }
        return true;
    }

    static validatePasswordMatch(password, confirmPassword) {
        if (password !== confirmPassword) {
            throw new Error('Passwords do not match');
        }
        return true;
    }

    static validateTime(startTime, endTime) {
        if (startTime >= endTime) {
            throw new Error('End time must be after start time');
        }
        return true;
    }
}

// ========================================
// Export for use in HTML files
// ========================================
if (typeof window !== 'undefined') {
    window.APIService = APIService;
    window.AuthHelper = AuthHelper;
    window.Utils = Utils;
    window.NavigationHelper = NavigationHelper;
    window.FormValidator = FormValidator;
    window.CONFIG = CONFIG;
}












// console.log("script.js loaded");

// // -------------------------------------------
// // API BASE URL
// // -------------------------------------------
// const API = "http://127.0.0.1:8000";


// // -------------------------------------------
// // LOGIN HANDLER
// // -------------------------------------------
// async function handleLogin(event) {
//     event.preventDefault();

//     const email = document.getElementById("email").value.trim();
//     const password = document.getElementById("password").value.trim();

//     try {
//         const res = await fetch(`${API}/auth/login`, {
//             method: "POST",
//             headers: { "Content-Type": "application/json" },
//             body: JSON.stringify({ email, password })
//         });

//         const data = await res.json();

//         if (!res.ok) {
//             alert(data.detail || "Invalid credentials");
//             return;
//         }

//         // Save token
//         localStorage.setItem("auth_token", data.access_token);

//         // Decode role
//         const payload = JSON.parse(atob(data.access_token.split(".")[1]));
//         localStorage.setItem("user_data", JSON.stringify(payload));

//         // Redirect by role
//         if (payload.role === "ADMIN") {
//             window.location.href = "admin.html";
//         } else {
//             window.location.href = "doctors.html";
//         }

//     } catch (err) {
//         console.error(err);
//         alert("Login failed");
//     }
// }

// if (document.getElementById("loginForm")) {
//     document.getElementById("loginForm").addEventListener("submit", handleLogin);
// }



// // -------------------------------------------
// // LOGOUT
// // -------------------------------------------
// function logout() {
//     localStorage.removeItem("auth_token");
//     localStorage.removeItem("user_data");
//     window.location.href = "login.html";
// }

// if (document.getElementById("logoutBtn")) {
//     document.getElementById("logoutBtn").addEventListener("click", logout);
// }



// // -------------------------------------------
// // PUBLIC DOCTOR LIST (patients)
// // -------------------------------------------
// async function loadDoctors() {

//     const list = document.getElementById("doctorList");
//     if (!list) return;

//     list.innerHTML = "Loading...";

//     try {
//         // FIXED: WRONG → /doctors/all  
//         const res = await fetch(`${API}/doctors/public`);
//         const doctors = await res.json();

//         list.innerHTML = "";

//         doctors.forEach(doc => {
//             const li = document.createElement("li");
//             li.textContent = `${doc.name} — ${doc.specialty}`;
//             list.appendChild(li);
//         });

//     } catch (err) {
//         console.error(err);
//         list.innerHTML = "Failed to load doctors.";
//     }
// }



// // -------------------------------------------
// // ADMIN DOCTOR LIST (protected)
// // -------------------------------------------
// async function loadAdminDoctors() {

//     const list = document.getElementById("adminDoctorList");
//     if (!list) return;

//     const token = localStorage.getItem("auth_token");
//     if (!token) {
//         window.location.href = "login.html";
//         return;
//     }

//     list.innerHTML = "Loading...";

//     try {
//         // FIXED: WRONG → /doctors/
//         const res = await fetch(`${API}/doctors/admin`, {
//             headers: { "Authorization": `Bearer ${token}` }
//         });

//         if (res.status === 401) {
//             alert("Session expired. Login again.");
//             logout();
//             return;
//         }

//         const data = await res.json();
//         list.innerHTML = "";

//         data.doctors.forEach(doc => {
//             const li = document.createElement("li");
//             li.textContent = `${doc.name} | ${doc.email} | ${doc.specialty}`;
//             list.appendChild(li);
//         });

//     } catch (err) {
//         console.error(err);
//         list.innerHTML = "Failed to load admin doctor data.";
//     }
// }



// // -------------------------------------------
// // AUTO PAGE LOADING
// // -------------------------------------------
// document.addEventListener("DOMContentLoaded", () => {
//     loadDoctors();
//     loadAdminDoctors();
// });
