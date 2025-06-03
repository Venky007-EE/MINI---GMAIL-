document.addEventListener('DOMContentLoaded', () => {
    console.log('Mini Gmail loaded');

    // Form validation for login and signup forms
    const loginForm = document.querySelector('form[action="/login"]');
    const signupForm = document.querySelector('form[action="/signup"]');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in both email and password fields.');
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value.trim();
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in both email and password fields.');
            } else if (!/\S+@\S+\.\S+/.test(email)) {
                e.preventDefault();
                alert('Please enter a valid email address.');
            }
        });
    }

    // Logout confirmation
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            if (!confirm('Are you sure you want to log out?')) {
                e.preventDefault();
            }
        });
    }

    // Toggle email body preview in inbox
    const inboxTable = document.querySelector('table');
    if (inboxTable) {
        const rows = inboxTable.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const subjectCell = row.cells[1]; // Subject column
            const emailBody = row.cells[1].dataset.body || 'No body available'; // Store body in dataset (requires backend update)
            
            const previewDiv = document.createElement('div');
            previewDiv.className = 'email-preview';
            previewDiv.innerText = emailBody;
            previewDiv.style.display = 'none';
            
            subjectCell.appendChild(previewDiv);
            subjectCell.style.cursor = 'pointer';
            
            subjectCell.addEventListener('click', () => {
                previewDiv.style.display = previewDiv.style.display === 'none' ? 'block' : 'none';
            });
        });
    }
});