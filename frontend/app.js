const API_URL = 'http://127.0.0.1:8000';
let currentAuthMode = 'login'; // 'login' or 'register'

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('orbit_token');
    const isDashboard = document.getElementById('dashboard-view') !== null;
    const isAuth = document.getElementById('auth-view') !== null;

    if (token) {
        if (isAuth) {
            window.location.href = 'dashboard.html';
        } else if (isDashboard) {
            loadDashboard();
        }
    } else {
        if (isDashboard) {
            window.location.href = 'index.html';
        }
    }
});

function switchAuth(mode) {
    currentAuthMode = mode;
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById('auth-btn').innerText = mode === 'login' ? 'Login' : 'Register';
    document.getElementById('auth-error').innerText = '';
}

// Auth API Calls
async function handleAuth(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('auth-error');
    const btn = document.getElementById('auth-btn');

    btn.innerText = 'Loading...';
    btn.disabled = true;

    try {
        if (currentAuthMode === 'register') {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (!res.ok) throw new Error(await getErrorMsg(res));
            // Auto login after register
            currentAuthMode = 'login';
            await handleAuth(e); 
        } else {
            // Login uses form-urlencoded
            const params = new URLSearchParams();
            params.append('username', email);
            params.append('password', password);

            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: params
            });
            if (!res.ok) throw new Error(await getErrorMsg(res));
            
            const data = await res.json();
            localStorage.setItem('orbit_token', data.access_token);
            window.location.href = 'dashboard.html';
        }
    } catch (err) {
        errorEl.innerText = err.message;
    } finally {
        btn.innerText = currentAuthMode === 'login' ? 'Login' : 'Register';
        btn.disabled = false;
    }
}

function logout() {
    localStorage.removeItem('orbit_token');
    window.location.href = 'index.html';
}

// Dashboard Data
async function fetchWithAuth(endpoint, options = {}) {
    const token = localStorage.getItem('orbit_token');
    if (!token) { logout(); return; }

    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        }
    });

    if (res.status === 401) { logout(); throw new Error("Session expired"); }
    return res;
}

async function loadDashboard() {
    await Promise.all([loadInsights(), loadExpenses(), loadSummary()]);
}

// Add Expense
async function addExpense(e) {
    e.preventDefault();
    const amount = parseFloat(document.getElementById('amount').value);
    const category = document.getElementById('category').value;
    const note = document.getElementById('note').value;
    const btn = e.target.querySelector('button');
    
    btn.innerText = 'Adding...';
    try {
        const res = await fetchWithAuth('/expenses/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, category, note })
        });
        if (res.ok) {
            document.getElementById('expense-form').reset();
            loadDashboard();
        }
    } catch(err) {
        console.error(err);
    } finally {
        btn.innerText = 'Add Expense';
    }
}

// Set Limit
async function setLimit(e) {
    e.preventDefault();
    const limit = parseFloat(document.getElementById('monthly-limit').value);
    try {
        const res = await fetchWithAuth('/limits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ monthly_limit: limit })
        });
        if (res.ok) {
            document.getElementById('limit-alert').innerText = "Limit saved!";
            setTimeout(() => document.getElementById('limit-alert').innerText = "", 3000);
            loadInsights(); // Reload alerts
        }
    } catch(err) { console.error(err); }
}

// Load Insights
async function loadInsights() {
    try {
        const res = await fetchWithAuth('/insights');
        const data = await res.json();
        
        if (data.message) {
            document.getElementById('total-spend').innerText = "Rs.0.00";
            return;
        }

        // Update Total
        document.getElementById('total-spend').innerText = `Rs.${data.total_last_30_days.toFixed(2)}`;

        // Update Bars
        const p = data.percentages;
        document.getElementById('pct-need').innerText = p.Need || 0;
        document.getElementById('pct-want').innerText = p.Want || 0;
        document.getElementById('pct-invest').innerText = p.Invest || 0;

        document.getElementById('bar-need').style.width = `${p.Need || 0}%`;
        document.getElementById('bar-want').style.width = `${p.Want || 0}%`;
        document.getElementById('bar-invest').style.width = `${p.Invest || 0}%`;

        // Update Insights
        const container = document.getElementById('insights-container');
        container.innerHTML = '';
        
        if (data.limit_alert) {
            container.innerHTML += `<div class="insight-badge" style="border-color: #ef4444; color: #ef4444;">🚨 ${data.limit_alert}</div>`;
        }

        data.insights.forEach(msg => {
            let color = 'var(--primary)';
            if(msg.includes('⚠️')) color = '#f59e0b';
            if(msg.includes('💪')) color = '#10b981';
            container.innerHTML += `<div class="insight-badge" style="border-color: ${color}">${msg}</div>`;
        });

    } catch(err) { console.error(err); }
}

// Load Expenses List
async function loadExpenses() {
    try {
        const res = await fetchWithAuth('/expenses/');
        const data = await res.json();
        const container = document.getElementById('expense-list');
        
        if (data.length === 0) {
            container.innerHTML = "<p style='color: var(--text-muted)'>No expenses yet.</p>";
            return;
        }

        container.innerHTML = data.map(exp => `
            <div class="expense-item">
                <div class="exp-info">
                    <strong class="cat-${exp.category}">${exp.category}</strong>
                    <span>${new Date(exp.date).toLocaleDateString()} ${exp.note ? ' • '+exp.note : ''}</span>
                </div>
                <div class="exp-amount">Rs.${exp.amount.toFixed(2)}</div>
            </div>
        `).join('');
    } catch(err) { console.error(err); }
}

// Spending Summary Logic
function handleSummaryTypeChange() {
    const type = document.getElementById('summary-type').value;
    const customRange = document.getElementById('custom-date-range');
    
    if (type === 'custom') {
        customRange.style.display = 'flex';
    } else {
        customRange.style.display = 'none';
        loadSummary();
    }
}

async function loadSummary() {
    const type = document.getElementById('summary-type').value;
    let endpoint = `/summary/${type}`;
    
    if (type === 'custom') {
        const start = document.getElementById('summary-start').value;
        const end = document.getElementById('summary-end').value;
        if (!start || !end) return; // Wait for both dates
        endpoint = `/summary/custom?start_date=${start}&end_date=${end}`;
    }

    try {
        const res = await fetchWithAuth(endpoint);
        const data = await res.json();
        
        document.getElementById('summary-total-display').innerText = `Rs.${(data.total_spending || 0).toFixed(2)}`;
        
        let dateText = "Today";
        if (type === 'monthly') dateText = "Last 30 Days";
        else if (type === 'custom') dateText = `${data.start_date} to ${data.end_date}`;
        
        document.getElementById('summary-date-range').innerText = dateText;
        
        const catContainer = document.getElementById('summary-categories');
        catContainer.innerHTML = '';
        
        if (data.categories) {
            for (const [cat, amt] of Object.entries(data.categories)) {
                catContainer.innerHTML += `
                    <div style="background: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${cat}</div>
                        <div style="font-weight: 600; color: white;">Rs.${amt.toFixed(2)}</div>
                    </div>
                `;
            }
        }
    } catch(err) { console.error(err); }
}

async function getErrorMsg(res) {
    try {
        const d = await res.json();
        return d.detail || JSON.stringify(d);
    } catch {
        return "An error occurred";
    }
}
