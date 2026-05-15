const API_URL = 'http://localhost:8000';
let currentToken = localStorage.getItem('token') || null;
let currentUserId = localStorage.getItem('user_id') || null;
let currentUser = null;

// DOM Elements
const authSection = document.getElementById('auth-section');
const blogSection = document.getElementById('blog-section');
const navActions = document.getElementById('nav-actions');
const postsContainer = document.getElementById('posts-container');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const adminDashboard = document.getElementById('admin-dashboard');
const createPostPanel = document.getElementById('create-post-panel');

// Initialize app state
function init() {
    updateUIBasedOnAuth();
}

// UI State Management
async function updateUIBasedOnAuth() {
    if (currentToken) {
        // Fetch full profile info
        try {
            const response = await fetch(`${API_URL}/me`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            });
            if (response.ok) {
                currentUser = await response.json();
                renderNavBar();
                authSection.classList.add('hidden');
                blogSection.classList.remove('hidden');
                
                // Show/Hide Admin Dashboard
                if (currentUser.role === 'admin') {
                    adminDashboard.classList.remove('hidden');
                    loadAdminUsers();
                } else {
                    adminDashboard.classList.add('hidden');
                }

                // Show/Hide Create Post Panel (Authors and Admins only)
                if (currentUser.role === 'admin' || currentUser.role === 'author') {
                    createPostPanel.classList.remove('hidden');
                } else {
                    createPostPanel.classList.add('hidden');
                }

                fetchPosts();
            } else {
                handleLogout();
            }
        } catch (err) {
            handleLogout();
        }
    } else {
        authSection.classList.remove('hidden');
        blogSection.classList.add('hidden');
        navActions.innerHTML = `
            <span style="color: var(--text-muted); font-size: 0.9rem;">Join the community</span>
        `;
    }
}

function renderNavBar() {
    if (!currentUser) return;
    navActions.innerHTML = `
        <div class="user-profile-nav">
            <div class="user-badge-info">
                <span class="user-name">${escapeHTML(currentUser.username)}</span>
                <span class="user-role-label">${currentUser.role}</span>
            </div>
            <button class="btn outline-btn" onclick="handleLogout()">Logout</button>
        </div>
    `;
}

async function loadAdminUsers() {
    const list = document.getElementById('admin-users-list');
    try {
        const response = await fetch(`${API_URL}/admin/users`, {
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        const users = await response.json();
        if (response.ok) {
            list.innerHTML = users.map(u => `
                <tr>
                    <td>${escapeHTML(u.username)}</td>
                    <td>${escapeHTML(u.email)}</td>
                    <td>
                        <select class="role-select-mini" onchange="updateUserRole(${u.id}, this.value)">
                            <option value="reader" ${u.role === 'reader' ? 'selected' : ''}>Reader</option>
                            <option value="author" ${u.role === 'author' ? 'selected' : ''}>Author</option>
                            <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
                        </select>
                    </td>
                    <td>
                        <button class="btn btn-sm outline-btn" onclick="deleteUser(${u.id})">Delete</button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.error('Admin users load failed');
    }
}

async function updateUserRole(userId, newRole) {
    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}/role`, {
            method: 'PUT',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ role: newRole })
        });
        if (response.ok) {
            alert('Role updated successfully');
            updateUIBasedOnAuth(); // Refresh
        } else {
            alert('Failed to update role');
        }
    } catch (err) {
        alert('Server error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Delete this user?')) return;
    try {
        const response = await fetch(`${API_URL}/admin/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        if (response.ok) {
            loadAdminUsers();
        }
    } catch (err) {
        alert('Error deleting user');
    }
}

function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(t => t.classList.remove('active'));
    
    if (tab === 'login') {
        tabs[0].classList.add('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    } else {
        tabs[1].classList.add('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    const submitBtn = event.target.querySelector('button');
    
    errorEl.textContent = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            console.log('Login successful, updating UI...');
            await updateUIBasedOnAuth();
            document.getElementById('login-password').value = '';
        } else {
            errorEl.textContent = data.detail || 'Login failed.';
        }
    } catch (err) {
        errorEl.textContent = 'Server error. Is the backend running?';
        console.error(err);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const errorEl = document.getElementById('reg-error');
    
    errorEl.textContent = '';
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('Registered successfully as Reader. Wait for Admin to promote you to Author if needed.');
            document.getElementById('login-email').value = email;
            document.getElementById('login-password').value = password;
            switchAuthTab('login');
        } else {
            errorEl.textContent = data.detail || 'Registration failed.';
        }
    } catch (err) {
        errorEl.textContent = 'Server error.';
    }
}

function handleLogout() {
    currentToken = null;
    localStorage.removeItem('token');
    updateUIBasedOnAuth();
}

// Blog Handlers
async function fetchPosts() {
    postsContainer.innerHTML = '<div class="loading-spinner"></div>';
    
    try {
        const response = await fetch(`${API_URL}/posts/?page=1&limit=50`);
        const posts = await response.json();
        
        if (response.ok) {
            renderPosts(posts);
        } else {
            postsContainer.innerHTML = `<p class="error-msg">Failed to load posts.</p>`;
        }
    } catch (err) {
        postsContainer.innerHTML = `<p class="error-msg">Server error. Make sure the backend is running.</p>`;
    }
}

function renderPosts(posts) {
    if (posts.length === 0) {
        postsContainer.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted);">
                <h3>No posts yet</h3>
                <p>Be the first to share your thoughts!</p>
            </div>
        `;
        return;
    }
    
    postsContainer.innerHTML = '';
    
    posts.forEach(post => {
        const card = document.createElement('div');
        card.className = 'post-card slide-up';
        
        card.innerHTML = `
            <h3 class="post-title">${escapeHTML(post.title)}</h3>
            <div class="post-content">${escapeHTML(post.content).replace(/\n/g, '<br>')}</div>
            <div class="post-meta">
                <span class="author-badge">Author ID: ${post.author_id}</span>
                <button class="delete-btn" onclick="deletePost(${post.id})">Delete</button>
            </div>
            <div class="post-footer">
                <div class="reactions-bar">
                    <button class="react-btn" onclick="handleReact(${post.id}, 'like')">👍 Like</button>
                    <button class="react-btn" onclick="handleReact(${post.id}, 'love')">❤️ Love</button>
                    <button class="react-btn" onclick="handleReact(${post.id}, 'haha')">😂 Haha</button>
                </div>
                <div class="comments-section" id="comments-${post.id}">
                    <!-- Comments loaded here -->
                </div>
                <div class="comment-input-group">
                    <input type="text" placeholder="Write a comment..." id="comment-input-${post.id}">
                    <button class="comment-btn" onclick="submitComment(${post.id})">Send</button>
                </div>
            </div>
        `;
        
        postsContainer.appendChild(card);
        loadComments(post.id);
    });
}

async function loadComments(postId) {
    const container = document.getElementById(`comments-${postId}`);
    try {
        const response = await fetch(`${API_URL}/posts/${postId}/comments`);
        const comments = await response.json();
        if (response.ok) {
            renderCommentsTree(comments, postId, container);
        }
    } catch (err) {
        console.error('Error loading comments', err);
    }
}

function renderCommentsTree(comments, postId, container) {
    // Organize comments into parent -> children map
    const map = {};
    const roots = [];
    
    comments.forEach(c => {
        map[c.id] = { ...c, children: [] };
    });
    
    comments.forEach(c => {
        if (c.parent_id && map[c.parent_id]) {
            map[c.parent_id].children.push(map[c.id]);
        } else {
            roots.push(map[c.id]);
        }
    });

    container.innerHTML = roots.map(c => renderCommentHTML(c, postId)).join('');
}

function renderCommentHTML(comment, postId, level = 0) {
    const indent = level * 20;
    const childrenHTML = comment.children.map(child => renderCommentHTML(child, postId, level + 1)).join('');
    
    return `
        <div class="comment-item" style="margin-left: ${indent}px; border-left: ${level > 0 ? '2px solid var(--primary)' : 'none'};">
            <div class="comment-author">User ID: ${comment.user_id}</div>
            <div class="comment-content">${escapeHTML(comment.content)}</div>
            <div style="margin-top: 5px;">
                <button class="react-btn" style="padding: 2px 8px; font-size: 0.7rem;" onclick="showReplyInput(${postId}, ${comment.id})">Reply</button>
            </div>
            <div id="reply-input-container-${comment.id}"></div>
            ${childrenHTML}
        </div>
    `;
}

function showReplyInput(postId, commentId) {
    const container = document.getElementById(`reply-input-container-${commentId}`);
    if (container.innerHTML !== '') {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = `
        <div class="comment-input-group" style="margin-top: 5px;">
            <input type="text" placeholder="Write a reply..." id="reply-input-${commentId}" style="font-size: 0.8rem;">
            <button class="comment-btn" style="padding: 0.3rem 0.8rem;" onclick="submitReply(${postId}, ${commentId})">Reply</button>
        </div>
    `;
}

async function submitReply(postId, commentId) {
    const input = document.getElementById(`reply-input-${commentId}`);
    const content = input.value.trim();
    if (!content) return;

    try {
        const response = await fetch(`${API_URL}/posts/${postId}/comments/${commentId}/reply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            loadComments(postId);
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to reply.');
        }
    } catch (err) {
        alert('Server error.');
    }
}

async function submitComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const content = input.value.trim();
    if (!content) return;

    try {
        const response = await fetch(`${API_URL}/posts/${postId}/comments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            input.value = '';
            loadComments(postId);
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to post comment. Make sure you are logged in.');
        }
    } catch (err) {
        alert('Server error.');
    }
}

async function handleReact(postId, type) {
    const btn = event.currentTarget;
    try {
        const response = await fetch(`${API_URL}/posts/${postId}/react`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ type })
        });

        if (response.ok) {
            const data = await response.json();
            // Visual feedback
            if (data.action === 'added' || data.action === 'changed') {
                btn.classList.add('active');
                // Remove active from siblings
                btn.parentNode.querySelectorAll('.react-btn').forEach(b => {
                    if (b !== btn) b.classList.remove('active');
                });
            } else {
                btn.classList.remove('active');
            }
        } else {
            const data = await response.json();
            alert(data.detail || 'Failed to react.');
        }
    } catch (err) {
        alert('Server error.');
    }
}

async function handleCreatePost(event) {
    event.preventDefault();
    const title = document.getElementById('post-title').value;
    const content = document.getElementById('post-content').value;
    const submitBtn = event.target.querySelector('button');
    const originalText = submitBtn.textContent;
    
    submitBtn.textContent = 'Publishing...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_URL}/posts/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ title, content })
        });
        
        if (response.ok) {
            document.getElementById('post-title').value = '';
            document.getElementById('post-content').value = '';
            fetchPosts();
        } else {
            const data = await response.json();
            alert(`Failed to create post: ${data.detail || 'Unauthorized'}`);
        }
    } catch (err) {
        alert('Server error. Try again later.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

async function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post?')) return;
    
    try {
        const response = await fetch(`${API_URL}/posts/${postId}`, {
            method: 'DELETE',
            headers: { 
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            fetchPosts();
        } else {
            const data = await response.json();
            alert(`Failed to delete post: ${data.detail || 'Unauthorized'}`);
        }
    } catch (err) {
        alert('Server error. Try again later.');
    }
}

// Utility
function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// Start
init();
